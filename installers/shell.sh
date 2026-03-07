#!/bin/bash
# ============================================================
#   installers/shell.sh — Shell environment setup (FIXED)
# ============================================================

ZSHRC_FILE="${HOME}/.zshrc"

install_shell() {
  section "Installing Shell Environment"
  echo ""

  # 1. Packages
  run_step "Installing git, unzip, zsh, fzf, zoxide" \
    $SUDO apt-get install -y git unzip zsh fzf zoxide

  # 2. Write ~/.zshrc (Simple & Clean)
  if [[ -f "$ZSHRC_FILE" ]]; then
    msg_info "Backing up existing .zshrc"
    cp "$ZSHRC_FILE" "${ZSHRC_FILE}.bak"
  fi

  _write_zshrc
  msg_ok "Configuration written to ${ZSHRC_FILE}"

  # 3. Zinit
  local zinit_dir="${HOME}/.local/share/zinit/zinit.git"
  if [[ ! -d "$zinit_dir" ]]; then
    run_step "Downloading Zinit Manager" \
      git clone --depth 1 https://github.com/zdharma-continuum/zinit.git "$zinit_dir"
  fi

  # 4. Set Default Shell (The Non-Blocking Way)
  local zsh_path
  zsh_path=$(command -v zsh)

  section "Finalizing Shell Setup"
  if [[ "$SHELL" == "$zsh_path" ]]; then
    msg_ok "Zsh is already your default shell"
  else
    msg_info "Setting Zsh as default (requires sudo)"
    # Use sudo to avoid interactive password prompt if already authenticated
    run_step "Changing default shell to Zsh" \
      $SUDO chsh -s "$zsh_path" "$USER"
  fi
}

_write_zshrc() {
  cat > "$ZSHRC_FILE" << 'ZSHRC'
# LARAVEL DEV SETUP — Managed Configuration
if [[ -r "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh" ]]; then
  source "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh"
fi

# Zinit Path
ZINIT_HOME="${XDG_DATA_HOME:-${HOME}/.local/share}/zinit/zinit.git"
source "${ZINIT_HOME}/zinit.zsh"

# Theme & Plugins
zinit ice depth=1; zinit light romkatv/powerlevel10k
zinit light zsh-users/zsh-syntax-highlighting
zinit light zsh-users/zsh-autosuggestions
zinit light Aloxaf/fzf-tab

# OMZ Snippets
zinit snippet OMZP::git
zinit snippet OMZP::sudo
zinit snippet OMZP::laravel

# Init Tools
[[ ! -f ~/.p10k.zsh ]] || source ~/.p10k.zsh
command -v zoxide &>/dev/null && eval "$(zoxide init zsh)"

# Path
export PATH="${HOME}/.config/composer/vendor/bin:${PATH}"
ZSHRC
}
