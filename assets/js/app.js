const TOOLTIP_CLASSES = ['hint--bottom', 'hint--large', 'hint--no-animate', 'override-hint-inline'];
const TOOLTIP_ATTRIBUTES_BY_RULE = {
  permissions: {
    heading: 'Permission',
    color: 'tooltip--permissions'
  },
  conditions: {
    heading: 'Condition',
    color: 'tooltip--conditions'
  },
  limitations: {
    heading: 'Limitation',
    color: 'tooltip--limitations'
  }
};

class Choosealicense {
  constructor() {
    this.initTooltips();
    this.initClipboard();
    this.initLicenseSuggestion();
  }

  // Selects the content of a given element
  selectText(element) {
    if (document.body.createTextRange) {
      const range = document.body.createTextRange();
      range.moveToElementText(element);
      range.select();
    } else if (window.getSelection) {
      const selection = window.getSelection();
      const range = document.createRange();

      range.selectNodeContents(element);
      selection.removeAllRanges();
      selection.addRange(range);
    }
  }

  // Init tooltip action
  initTooltips() {
    const annotations = window.annotations || {};

    Object.entries(annotations).forEach(([ruletype, rules]) => {
      rules.forEach((rule) => {
        const tooltipAttr = TOOLTIP_ATTRIBUTES_BY_RULE[ruletype];
        if (!tooltipAttr) return;

        const elements = Array.from(
          document.querySelectorAll(`.license-${ruletype} .${rule.tag}`)
        ).filter((el) => !el.closest(`dd.license-${ruletype}`));

        elements.forEach((el) => {
          el.setAttribute(
            'aria-label',
            `${rule.label} ${tooltipAttr.heading.toLowerCase()}: ${rule.description}`
          );
          el.classList.add(...TOOLTIP_CLASSES, tooltipAttr.color);
        });
      });
    });
  }

  // Initializes Clipboard.js
  initClipboard() {
    const buttons = document.querySelectorAll('.js-clipboard-button');
    buttons.forEach((button) => {
      button.dataset.clipboardPrompt = button.textContent;
    });

    const clip = new Clipboard('.js-clipboard-button');
    clip.on('mouseout', (event) => this.clipboardMouseout(event));
    clip.on('complete', (event) => this.clipboardComplete(event));
  }

  // Callback to restore the clipboard button's original text
  clipboardMouseout(event) {
    const trigger = event && event.trigger;
    if (trigger) {
      trigger.textContent = trigger.dataset.clipboardPrompt || '';
    }
  }

  // Post-copy user feedback callback
  clipboardComplete(event) {
    const trigger = event && event.trigger;
    if (trigger) {
      trigger.textContent = 'Copied!';
    }
  }

  // Initializes the repository suggestion feature
  initLicenseSuggestion() {
    const inputEl = document.querySelector('#repository-url');
    const statusIndicator = document.querySelector('.status-indicator');
    if (!inputEl || !statusIndicator) return;

    const licenseId = inputEl.getAttribute('data-license-id');
    new LicenseSuggestion(inputEl, licenseId, statusIndicator);
  }
}

class LicenseSuggestion {
  constructor(inputEl, licenseId, statusIndicator) {
    this.inputEl = inputEl;
    this.licenseId = licenseId;
    this.statusIndicator = statusIndicator;
    this.inputWrapper = document.querySelector('.input-wrapper');
    this.tooltipErrorClasses = ['hint--bottom', 'tooltip--error', 'hint--always'];

    this.bindEventHandlers();
  }

  // Main event handlers for user input
  bindEventHandlers() {
    this.inputEl.addEventListener('input', () => {
      this.setStatus('');
    });

    this.inputEl.addEventListener('keyup', (event) => {
      if (event.key !== 'Enter' || !event.target.value) return;

      let repositoryFullName;
      try {
        repositoryFullName = this.parseUserInput(event.target.value);
      } catch (error) {
        this.setStatus('Error', 'Invalid URL.');
        return;
      }

      this.setStatus('Fetching');
      this.fetchInfoFromGithubAPI(repositoryFullName, (err, repositoryInfo = null) => {
        if (err) {
          this.setStatus('Error', err.message);
          return;
        }
        if (repositoryInfo.license) {
          const license = repositoryInfo.license;
          this.setStatus('Error', this.repositoryLicense(repositoryFullName, license));
        } else {
          const licenseUrl = encodeURIComponent(
            `https://github.com/${repositoryFullName}/community/license/new?template=${this.licenseId}`
          );
          window.location.href = `https://github.com/login?return_to=${licenseUrl}`;
          this.setStatus('');
          this.inputEl.value = '';
        }
      });
    });
  }

  // Try to extract the repository full name from the user input
  parseUserInput(userInput) {
    const repository = /https?:\/\/github\.com\/([^\/]+)\/([^\/?#]+)/.exec(userInput);
    if (!repository) throw new Error('Invalid URL.');

    const [, username, project] = repository;
    return `${username}/${project.replace(/(\.git)$/, '')}`;
  }

  // Displays an indicator and tooltips to the user about the current status
  setStatus(status = '', message = '') {
    const statusClass = status.toLowerCase();
    const displayTooltip = (s, m) => {
      if (!this.inputWrapper) return;
      this.inputWrapper.setAttribute('aria-label', `${s}: ${m}`);
      this.inputWrapper.classList.add(...this.tooltipErrorClasses);
    };

    switch (status) {
      case 'Fetching':
        this.statusIndicator.classList.remove('error', ...this.tooltipErrorClasses);
        this.statusIndicator.classList.add(statusClass);
        break;
      case 'Error':
        this.statusIndicator.classList.remove('fetching');
        this.statusIndicator.classList.add(statusClass);
        displayTooltip(status, message);
        break;
      default:
        this.statusIndicator.classList.remove('fetching', 'error');
        if (this.inputWrapper) {
          this.inputWrapper.classList.remove(...this.tooltipErrorClasses);
        }
        break;
    }
  }

  // Fetches information about a repository from the Github API
  fetchInfoFromGithubAPI(repositoryFullName, callback) {
    fetch(`https://api.github.com/repos/${repositoryFullName}`)
      .then((response) => {
        if (!response.ok) {
          if (response.status === 404) {
            throw new Error(`Repository ${repositoryFullName} not found.`);
          }
          throw new Error(`Network error when trying to get information about ${repositoryFullName}.`);
        }
        return response.json();
      })
      .then((info) => callback(null, info))
      .catch((error) => callback(error));
  }

  // Generates a message showing that a repository is already licensed
  repositoryLicense(repositoryFullName, license) {
    const foundLicense = window.licenses.find((lic) => lic.spdx_id === license.spdx_id);
    if (foundLicense) {
      return `The repository ${repositoryFullName} is already licensed under the ${foundLicense.title}.`;
    }
    return `The repository ${repositoryFullName} is already licensed.`;
  }
}

document.addEventListener('DOMContentLoaded', () => {
  new Choosealicense();
});
