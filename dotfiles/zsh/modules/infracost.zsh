if [[ -r ~/.infracost_api_key ]]; then
    export INFRACOST_API_KEY="$(<~/.infracost_api_key)"
else
    print -u2 "infracost module: no ~/.infracost_api_key file"
    return 1
fi
