#Aliases
alias gvim="UBUNTU_MENUPROXY= gvim"

#configs
export EDITOR="vim"

export PATH=$PATH:/home/schillb/bin

#colored manpages
export LESS_TERMCAP_mb=$'\E[01;31m'
export LESS_TERMCAP_md=$'\E[01;31m'
export LESS_TERMCAP_me=$'\E[0m'
export LESS_TERMCAP_se=$'\E[0m'
export LESS_TERMCAP_so=$'\E[01;44;33m'
export LESS_TERMCAP_ue=$'\E[0m'
export LESS_TERMCAP_us=$'\E[01;32m'


. ~/.to.sh

if [ -x /usr/bin/dircolors ]; then
    test -r ~/.dircolors && eval "$(dircolors -b ~/.dircolors)" || eval "$(dircolors -b)"
    alias ls='ls --color=auto'
    alias grep='grep --color=auto'
fi

#define say function only if not already defined.
if [ ! $(which say) ]; then
    say() { if [[ "${1}" =~ -[a-z]{2} ]]; then local lang=${1#-}; local text="${*#$1}"; else local lang=${LANG%_*}; local text="$*";fi; mplayer "http://translate.google.com/translate_tts?ie=UTF-8&tl=${lang}&q=${text}" &> /dev/null ; }
fi

# define colors
Black='\e[0;30m'    # Black / Regular
Red='\e[0;31m'      # Red
Green='\e[0;32m'    # Green
Yellow='\e[0;33m'   # Yellow
Blue='\e[0;34m'     # Blue
Purple='\e[0;35m'   # Purple
Cyan='\e[0;36m'     # Cyan
White='\e[0;37m'    # White

NC='\e[0m'          # Text Reset / No Color

function exitstatus {

        EXITSTATUS="$?"

        if [ "$EXITSTATUS" -eq "0" ]
        then
                #PS1="\[$(tput bold)\]\[$(tput setaf 1)\]\h\[$(tput setaf 6)\]/\W\[$(tput setaf 2)\] :) $\[$(tput sgr0)\] "
                PS1="\[\033[36m\]\u\[\033[m\]@\[\033[33;1m\]\h:\[$Green\]\W :) $\[\033[m\] "
                #PS1="\[\033[36m\]\u\[\033[m\]@\[\033[32m\]\h:\[\033[33;1m\]\W :) $\[\033[m\] "
        else
                #PS1="\[$(tput bold)\]\[$(tput setaf 1)\]\h\[$(tput setaf 6)\]/\W\[$(tput setaf 1)\] :( $\[$(tput sgr0)\] "
                PS1="\[\033[36m\]\u\[\033[m\]@\[\033[33;1m\]\h:\[$Red\]\W :( $\[\033[m\] "
                #PS1="\[\033[36m\]\u\[\033[m\]@\[\033[32m\]\h:\[ $Red \]\W :( $\[ $NC \] "
        fi

}
#prompt commented out in favor of exitstatus prompt
#export PS1="\[\033[36m\]\u\[\033[m\]@\[\033[32m\]\h:\[\033[33;1m\]\w\[\033[m\]\$ "

PROMPT_COMMAND=exitstatus


function extract()      # Handy Extract Program
{
    if [ -f $1 ] ; then
        case $1 in
            *.tar.bz2)   tar xvjf $1     ;;
            *.tar.gz)    tar xvzf $1     ;;
            *.bz2)       bunzip2 $1      ;;
            *.rar)       unrar x $1      ;;
            *.gz)        gunzip $1       ;;
            *.tar)       tar xvf $1      ;;
            *.tbz2)      tar xvjf $1     ;;
            *.tgz)       tar xvzf $1     ;;
            *.zip)       unzip $1        ;;
            *.Z)         uncompress $1   ;;
            *.7z)        7z x $1         ;;
            *)           echo "'$1' cannot be extracted via >extract<" ;;
        esac
    else
        echo "'$1' is not a valid file!"
    fi
}