#!/usr/bin/env bash
# Publie ce répertoire de skills sur GitHub.
#
# Prérequis : créer d'abord un dépôt VIDE sur https://github.com/new
# (sans README, sans .gitignore, sans licence), de préférence privé.
#
# Usage :
#   bash push_github.sh <url-du-depot> [branche] ["message de commit"]
# Exemples :
#   bash push_github.sh git@github.com:mon-compte/skills-ohada.git
#   bash push_github.sh https://github.com/mon-compte/skills-ohada.git main "Mise à jour des skills"
#   bash push_github.sh git@github.com:mon-compte/skills-ohada.git "Mise à jour des skills"   (branche main)
#
# Relançable : aux exécutions suivantes, il commite les nouveaux changements et pousse.

set -euo pipefail

URL="${1:-}"
BRANCHE="${2:-main}"
MESSAGE="${3:-Mise à jour des skills OHADA / UEMOA}"

# Tolérance : si le 2e argument n'est pas un nom de branche valide, c'est le message de commit.
if [[ -n "${2:-}" ]] && ! git check-ref-format --branch "$2" >/dev/null 2>&1; then
  MESSAGE="$2"
  BRANCHE="${3:-main}"
fi

if [[ -z "$URL" ]]; then
  echo "Usage : bash push_github.sh <url-du-depot> [branche] [\"message\"]" >&2
  exit 1
fi

cd "$(dirname "$0")"

# 1. Identité git
if ! git config user.name >/dev/null || ! git config user.email >/dev/null; then
  echo "Identité git manquante. Configurez-la puis relancez :" >&2
  echo "  git config --global user.name \"Votre nom\"" >&2
  echo "  git config --global user.email \"vous@exemple.com\"" >&2
  exit 1
fi

# 2. Initialisation du dépôt local
if [[ ! -d .git ]]; then
  git init -b "$BRANCHE"
  echo "Dépôt git initialisé (branche $BRANCHE)."
fi

# 3. Nettoyage des fichiers générés par Python
find . -name "__pycache__" -type d -prune -exec rm -rf {} +

# 4. Commit des changements
git add -A
if git diff --cached --quiet; then
  echo "Aucun changement à commiter."
else
  echo "Fichiers inclus dans le commit :"
  git diff --cached --name-status
  git commit -m "$MESSAGE"
fi

# 5. Remote origin
if git remote get-url origin >/dev/null 2>&1; then
  if [[ "$(git remote get-url origin)" != "$URL" ]]; then
    git remote set-url origin "$URL"
    echo "Remote origin mis à jour : $URL"
  fi
else
  git remote add origin "$URL"
  echo "Remote origin ajouté : $URL"
fi

# 6. Push
git branch -M "$BRANCHE"
git push -u origin "$BRANCHE"

echo
echo "Publié sur $URL (branche $BRANCHE)."
