#!/usr/bin/env bash
# Roda a suite da etapa 1 e imprime uma linha de resumo.
cd "$(dirname "$0")/.." || exit 2
python3 tests/gerar_dados.py || exit 2
python3 -m pytest tests -q -p no:cacheprovider --no-header -rfs "$@" > /tmp/raiox_testes.log 2>&1 ; COD=$?
tail -40 /tmp/raiox_testes.log
echo "RESUMO: $(tail -1 /tmp/raiox_testes.log)"
exit $COD
