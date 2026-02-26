#!/bin/bash

URL="http://localhost:8080/"
SIZE=$((50 * 1024 * 1024))
CONCURRENT_REQUESTS=150

send_request() {
  head -c "$SIZE" /dev/zero | \
  curl -X POST \
       -H "Content-Type: application/octet-stream" \
       --data-binary @- \
       "$URL" \
       -o /dev/null \
       -s
}

for i in $(seq 1 $CONCURRENT_REQUESTS); do
  send_request &
done

wait

echo "All requests completed."
