#!/bin/bash
cd "/Users/marcusquek/Documents/RF Physics"
for f in kb/*/*.md; do case $f in *_index.md|*_sources.md) continue;; esac
  echo "=== $f"; awk '/^## Questions this page answers/{f=1;next} /^## /{f=0} f' "$f" | grep -v '^\s*$' | cut -c1-200; done
