#!/bin/bash
# ============================================================
#   lib/shell.sh — Shell environment setup
#
#   Installs : git  unzip  zsh  fzf  zoxide
#   Configures: ~/.zshrc con zinit + powerlevel10k + plugins
#   Sets zsh as default shell for the current user
# ============================================================

ZSHRC_FILE="${HOME}/.zshrc"
ZSHRC_BACKUP="${HOME}/.zshrc.bak.$(date +%Y%m%d_%H%M%S)"

# ─────────────────────────────────────────────────────────────
#   Main entry point
# ─────────────────────────────────────────────────────────────
install_shell() {

  # ── 1. System packages ───────────────────────────────────
  section "Installing Shell Dependencies"
  echo ""
  msg_info "Packages: git  unzip  zsh  fzf  zoxide"
  echo ""

  run_step "Installing git unzip zsh fzf zoxide" \
    $SUDO apt-get install -y git unzip zsh fzf zoxide

  # ── 2. Write ~/.zshrc ────────────────────────────────────
  section "Configuring ~/.zshrc"
  echo ""

  if [[ -f "$ZSHRC_FILE" ]]; then
    msg_warn "Existing ~/.zshrc found — backing up to ${ZSHRC_BACKUP}"
    cp "$ZSHRC_FILE" "$ZSHRC_BACKUP"
    msg_ok "Backup saved: ${ZSHRC_BACKUP}"
    echo ""
  fi

  _write_zshrc
  msg_ok "~/.zshrc written"

  # ── 3. Pre-install zinit (clone now so first launch is fast)
  section "Installing Zinit Plugin Manager"
  echo ""

  local zinit_dir="${HOME}/.local/share/zinit/zinit.git"
  if [[ -d "$zinit_dir" ]]; then
    msg_info "Zinit already cloned at ${zinit_dir}"
  else
    run_step "Cloning zinit" \
      git clone https://github.com/zdharma-continuum/zinit.git "$zinit_dir"
  fi
  msg_ok "Zinit ready — plugins will download on first zsh launch"

  # ── 4. Set zsh as default shell ──────────────────────────
  section "Setting Zsh as Default Shell"
  echo ""

  local zsh_path
  zsh_path=$(command -v zsh)

  # Ensure zsh is in /etc/shells
  if ! grep -qx "$zsh_path" /etc/shells 2>/dev/null; then
    run_step "Adding ${zsh_path} to /etc/shells" \
      bash -c "echo '${zsh_path}' | $SUDO tee -a /etc/shells > /dev/null"
  else
    msg_ok "${zsh_path} already in /etc/shells"
  fi

  if [[ "$SHELL" == "$zsh_path" ]]; then
    msg_ok "Zsh is already your default shell"
  else
    run_step "Changing default shell to zsh (chsh)" \
      bash -c "chsh -s '${zsh_path}' '${USER}'"
    msg_ok "Default shell set to ${zsh_path}"
    msg_warn "Restart your terminal (or log out/in) to start using zsh"
  fi

  echo ""
  msg_info "First launch: zinit will auto-install powerlevel10k and plugins"
  msg_info "Run 'p10k configure' to customize your prompt"
}

# ─────────────────────────────────────────────────────────────
#   Write the full ~/.zshrc
# ─────────────────────────────────────────────────────────────
_write_zshrc() {
  cat > "$ZSHRC_FILE" << 'ZSHRC'
# ============================================================
#   ~/.zshrc — Zsh configuration
#   Managed by: install.sh
#   Reference : https://phoenixnap.com/kb/powerlevel10k
# ============================================================

# Enable Powerlevel10k instant prompt.
# Initialization code that may require console input (password
# prompts, [y/n] confirmations, etc.) must go above this block.
if [[ -r "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh" ]]; then
  source "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh"
fi

# macOS Homebrew (no-op on Linux)
if [[ -f "/opt/homebrew/bin/brew" ]]; then
  eval "$(/opt/homebrew/bin/brew shellenv)"
fi

# ── Zinit ────────────────────────────────────────────────────
ZINIT_HOME="${XDG_DATA_HOME:-${HOME}/.local/share}/zinit/zinit.git"

if [ ! -d "$ZINIT_HOME" ]; then
  mkdir -p "$(dirname $ZINIT_HOME)"
  git clone https://github.com/zdharma-continuum/zinit.git "$ZINIT_HOME"
fi

source "${ZINIT_HOME}/zinit.zsh"

# ── Theme: Powerlevel10k ──────────────────────────────────────
zinit ice depth=1; zinit light romkatv/powerlevel10k

# ── Plugins ───────────────────────────────────────────────────
zinit light zsh-users/zsh-syntax-highlighting
zinit light zsh-users/zsh-completions
zinit light zsh-users/zsh-autosuggestions
zinit light Aloxaf/fzf-tab

# ── OMZ Snippets ──────────────────────────────────────────────
zinit snippet OMZL::git.zsh
zinit snippet OMZP::git
zinit snippet OMZP::sudo
zinit snippet OMZP::laravel
zinit snippet OMZP::command-not-found

# ── Completions ───────────────────────────────────────────────
autoload -Uz compinit && compinit
zinit cdreplay -q

# ── Powerlevel10k config ──────────────────────────────────────
[[ ! -f ~/.p10k.zsh ]] || source ~/.p10k.zsh

# ── Keybindings ───────────────────────────────────────────────
bindkey -e
bindkey '^p' history-search-backward
bindkey '^n' history-search-forward
bindkey '^[w' kill-region

# ── History ───────────────────────────────────────────────────
HISTSIZE=5000
HISTFILE=~/.zsh_history
SAVEHIST=$HISTSIZE
HISTDUP=erase
setopt appendhistory
setopt sharehistory
setopt hist_ignore_space
setopt hist_ignore_all_dups
setopt hist_save_no_dups
setopt hist_ignore_dups
setopt hist_find_no_dups

# ── Completion styling ────────────────────────────────────────
zstyle ':completion:*' matcher-list 'm:{a-z}={A-Za-z}'
zstyle ':completion:*' list-colors "${(s.:.)LS_COLORS}"
zstyle ':completion:*' menu no
zstyle ':fzf-tab:complete:cd:*' fzf-preview 'ls --color $realpath'
zstyle ':fzf-tab:complete:__zoxide_z:*' fzf-preview 'ls --color $realpath'

# ── Zoxide (smarter cd) ───────────────────────────────────────
if command -v zoxide &>/dev/null; then
  eval "$(zoxide init zsh)"
fi

# ── NVM ───────────────────────────────────────────────────────
export NVM_DIR="${HOME}/.nvm"
[ -s "${NVM_DIR}/nvm.sh" ] && source "${NVM_DIR}/nvm.sh"
[ -s "${NVM_DIR}/bash_completion" ] && source "${NVM_DIR}/bash_completion"

# ── Composer global binaries ──────────────────────────────────
export PATH="${HOME}/.config/composer/vendor/bin:${PATH}"

# ── Aliases ───────────────────────────────────────────────────
alias ls='ls --color'
alias vim='nvim'
alias c='clear'
ZSHRC
}