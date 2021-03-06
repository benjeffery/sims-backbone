npm install @openapitools/openapi-generator-cli@cli-4.0.0-beta2 -D
for i in "$@"
do
case $i in
    server)
    SERVER_ONLY=true
    ;;
    client)
    CLIENT_ONLY=true
    ;;
    *)
          # unknown option
    ;;
esac
done
export PYTHON_POST_PROCESS_FILE="$(which yapf) -i"
if [ -n "$SERVER_ONLY" -o -z "$CLIENT_ONLY" ]
then
    rm -rf python-flask-server
    (cd openapi && npx openapi-generator generate -i sims-backbone.yaml -g python-flask -o ../python-flask-server --enable-post-process-file)
    sed -i  -e '/x-tokenInfoFunc/d' -e '/x-scopeValidateFunc/d' python-flask-server/openapi_server/openapi/openapi.yaml
    rm -rf server/bb_server
    cp -pr python-flask-server server/bb_server
fi
if [ -n "$CLIENT_ONLY" -o -z "$SERVER_ONLY" ]
then
    (cd openapi && npx openapi-generator generate -i sims-backbone.yaml -g typescript-angular -o ../client/sims-backbone/src/app/typescript-angular-client  -c client.config.json)
    rm -rf python_client
    (cd openapi && npx openapi-generator generate -i sims-backbone.yaml -g python -o ../python_client --enable-post-process-file)
fi
