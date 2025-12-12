// SPDX-FileCopyrightText: 2025 Chayan Das <01chayandas@gmail.com>
// SPDX-License-Identifier: GPL-2.0-only

package email

import (
	"context"
	"errors"
	"fmt"
	"os"
	"strconv"
	"sync"
	"time"

	"go.uber.org/zap"
	"gopkg.in/gomail.v2"
)

type EmailData struct {
	To      []string
	Cc      []string
	Bcc     []string
	Subject string
	HTML    string
}

type EmailService interface {
	enqueue(ctx context.Context, email EmailData) error
	enqueueAsync(data EmailData)
	Start()
	Stop(ctx context.Context) error
}

type AsyncEmailService struct {
	queue      chan EmailData
	from       string
	user       string
	pass       string
	host       string
	port       int
	logger     *zap.Logger
	wg         sync.WaitGroup
	maxRetries int
	retryDelay time.Duration
}

const (
	defaultQueueSize   = 200
	defaultWorkerCount = 5
	defaultMaxRetries  = 3
	defaultRetryDelay  = 5 * time.Second
)

func NewEmailService(from, smtpUser, pass, host string, port int, opts ...func(*AsyncEmailService)) EmailService {
	logger, _ := zap.NewProduction()

	s := &AsyncEmailService{
		queue:      make(chan EmailData, defaultQueueSize),
		from:       from,
		user:       smtpUser,
		pass:       pass,
		host:       host,
		port:       port,
		logger:     logger,
		maxRetries: defaultMaxRetries,
		retryDelay: defaultRetryDelay,
	}

	for _, o := range opts {
		o(s)
	}

	return s
}

// Start workers
func (s *AsyncEmailService) Start() {
	s.logger.Info("Starting email service",
		zap.Int("workers", defaultWorkerCount),
		zap.Int("queue_capacity", cap(s.queue)),
		zap.Int("max_retries", s.maxRetries),
		zap.Duration("retry_delay", s.retryDelay),
	)

	for i := 0; i < defaultWorkerCount; i++ {
		s.wg.Add(1)
		go s.worker(i)
	}
}

// enqueue enqueues email data for processing with context
func (s *AsyncEmailService) enqueue(ctx context.Context, email EmailData) error {
	if len(email.To) == 0 {
		return errors.New("missing recipient")
	}

	select {
	case <-ctx.Done():
		return ctx.Err()
	case s.queue <- email:
		return nil
	}
}

// enqueueAsync enqueues email data for asynchronous processing( without context )
func (s *AsyncEmailService) enqueueAsync(data EmailData) {
	if Email == nil {
		return
	}

	go func() {
		ctx, cancel := context.WithTimeout(context.Background(), 3*time.Second)
		defer cancel()
		_ = s.enqueue(ctx, data)
	}()
}

func (s *AsyncEmailService) worker(id int) {
	defer s.wg.Done()
	s.logger.Info("worker started", zap.Int("id", id))

	for email := range s.queue {
		s.processWithRetries(email)
	}

	s.logger.Info("worker stopped", zap.Int("id", id))
}

func (s *AsyncEmailService) processWithRetries(job EmailData) {
	for attempt := 1; attempt <= s.maxRetries; attempt++ {
		if err := s.doSend(job); err != nil {
			s.logger.Warn("email send failed",
				zap.Int("attempt", attempt),
				zap.Strings("to", job.To),
				zap.Error(err),
			)

			if attempt < s.maxRetries {
				time.Sleep(s.retryDelay)
			}
			continue
		}

		s.logger.Info("email sent successfully",
			zap.Strings("to", job.To),
			zap.String("subject", job.Subject),
		)
		return
	}

	s.logger.Error("email permanently failed after retries",
		zap.Strings("to", job.To),
	)
}

func (s *AsyncEmailService) doSend(job EmailData) error {
	msg := gomail.NewMessage()
	msg.SetHeader("From", s.from)
	msg.SetHeader("To", job.To...)
	if len(job.Cc) > 0 {
		msg.SetHeader("Cc", job.Cc...)
	}
	if len(job.Bcc) > 0 {
		msg.SetHeader("Bcc", job.Bcc...)
	}
	msg.SetHeader("Subject", job.Subject)
	msg.SetBody("text/html", job.HTML)

	username := s.user
	if username == "" {
		username = s.from
	}

	// Set up the dialer
	d := gomail.NewDialer(s.host, s.port, username, s.pass)

	// Send the email
	if err := d.DialAndSend(msg); err != nil {
		return fmt.Errorf("gomail error: %w", err)
	}
	return nil
}

// Stop gracefully shuts down the workers
func (s *AsyncEmailService) Stop(ctx context.Context) error {
	close(s.queue)

	done := make(chan struct{})
	go func() {
		s.wg.Wait()
		close(done)
	}()

	select {
	case <-done:
		s.logger.Info("email service stopped gracefully")
		return nil
	case <-ctx.Done():
		return ctx.Err()
	}
}

var Email EmailService

func Init() error {
	user := os.Getenv("SMTP_USER")
	pass := os.Getenv("SMTP_PASSWORD")
	host := os.Getenv("SMTP_HOST")
	portStr := os.Getenv("SMTP_PORT")
	from := os.Getenv("SMTP_FROM")

	if from == "" {
		from = user
	}

	if user == "" || pass == "" || host == "" || portStr == "" || from == "" {
		return fmt.Errorf("missing SMTP environment variables")
	}

	port, err := strconv.Atoi(portStr)
	if err != nil {
		return fmt.Errorf("invalid SMTP_PORT: %w", err)
	}

	svc := NewEmailService(from, user, pass, host, port)
	Email = svc
	Email.Start()
	return nil
}
