#
# ~/.bashrc
#

# If not running interactively, don't do anything
[[ $- != *i* ]] && return

alias ls='ls --color=auto'
PS1='[\u@\h \W]\$ '

export LANG="fr_FR.UTF-8"

alias rm='rm -i'
alias cp='cp -i'
alias mv='mv -i'
alias vi=vim
