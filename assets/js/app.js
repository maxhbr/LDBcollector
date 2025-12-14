class Choosealicense {
  constructor() {
    this.tooltipAttributesMapperByRuleType = {
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
        const licenseLiElement = $(`.license-${ruletype} .${rule.tag}`).not(
          `dd.license-${ruletype} .${rule.tag}`
        );
        const tooltipAttr = this.tooltipAttributesMapperByRuleType[ruletype];
        if (!tooltipAttr) return;

        licenseLiElement.attr(
          'aria-label',
          `${rule.label} ${tooltipAttr.heading.toLowerCase()}: ${rule.description}`
        );
        licenseLiElement.addClass(
          `hint--bottom
                                   hint--large
                                   hint--no-animate
                                   ${tooltipAttr.color}
                                   override-hint-inline`
        );
      });
    });
  }

  // Initializes Clipboard.js
  initClipboard() {
    const clipboardPrompt = $('.js-clipboard-button').text();
    $('.js-clipboard-button').data('clipboard-prompt', clipboardPrompt);

    const clip = new Clipboard('.js-clipboard-button');
    clip.on('mouseout', this.clipboardMouseout);
    clip.on('complete', this.clipboardComplete);
  }

  // Callback to restore the clipboard button's original text
  clipboardMouseout(client, args) {
    this.textContent = $(this).data('clipboard-prompt');
  }

  // Post-copy user feedback callback
  clipboardComplete(client, args) {
    this.textContent = 'Copied!';
  }

  // Initializes the repository suggestion feature
  initLicenseSuggestion() {
    const inputEl = $('#repository-url');
    const licenseId = inputEl.attr('data-license-id');
    const statusIndicator = $('.status-indicator');
    new LicenseSuggestion(inputEl, licenseId, statusIndicator);
  }
}

class LicenseSuggestion {
  constructor(inputEl, licenseId, statusIndicator) {
    this.inputEl = inputEl;
    this.licenseId = licenseId;
    this.statusIndicator = statusIndicator;
    this.inputWrapper = $('.input-wrapper');
    this.tooltipErrorClasses = 'hint--bottom tooltip--error hint--always';

    this.bindEventHandlers();
  }

  // Main event handlers for user input
  bindEventHandlers() {
    this.inputEl
      .on('input', () => {
        this.setStatus('');
      })
      .on('keyup', (event) => {
        if (event.keyCode === 13 && event.target.value) {
          let repositoryFullName;
          try {
            repositoryFullName = this.parseUserInput(event.target.value);
          } catch (error) {
            this.setStatus('Error', 'Invalid URL.');
            return;
          }

          this.setStatus('Fetching');
          this.fetchInfoFromGithubAPI(
            repositoryFullName,
            (err, repositoryInfo = null) => {
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
                this.inputEl.val('');
              }
            }
          );
        }
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
      this.inputWrapper.attr('aria-label', `${s}: ${m}`);
      this.inputWrapper.addClass(this.tooltipErrorClasses);
    };

    switch (status) {
      case 'Fetching':
        this.statusIndicator.removeClass(`error ${this.tooltipErrorClasses}`).addClass(statusClass);
        break;
      case 'Error':
        this.statusIndicator.removeClass('fetching').addClass(statusClass);
        displayTooltip(status, message);
        break;
      default:
        this.statusIndicator.removeClass('fetching error');
        this.inputWrapper.removeClass(this.tooltipErrorClasses);
        break;
    }
  }

  // Fetches information about a repository from the Github API
  fetchInfoFromGithubAPI(repositoryFullName, callback) {
    $.getJSON(`https://api.github.com/repos/${repositoryFullName}`, (info) => {
      callback(null, info);
    }).fail((e) => {
      if (e.status === 404) {
        callback(new Error(`Repository ${repositoryFullName} not found.`));
      } else {
        callback(new Error(`Network error when trying to get information about ${repositoryFullName}.`));
      }
    });
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

$(() => {
  new Choosealicense();
});
