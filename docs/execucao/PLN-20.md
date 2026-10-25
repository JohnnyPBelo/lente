# Ordem de trabalho PLN-20

Fonte: `docs/planos/PLN-20-diario-etiquetas-e-copia-de-seguranca.md`. Este ramo não implementa a aplicação. A implementação entra depois, no mesmo pull request, quando as dependências estiverem fundidas e os caminhos de **Não tocar** forem respeitados.

## Objectivo

Diário local append-only (procuras, documentos abertos, feedback, fechos de dossier); etiquetas manuais em documentos com filtro na biblioteca (sugestão de tipo por embedding continua só sugestão); acção de backup: zip da pasta `data/` para caminho escolhido, sem nuvem.

## Fronteira

o que NÃO entra neste plano — contas, rede de sync, edição/apagamento do diário, backup incremental remoto.

## Teste que falha primeiro, no plano

`tests/diario/test_append.py` — após registar procura e feedback, `ler_diario` devolve as entradas em ordem; tentativa de `UPDATE`/`DELETE` via API do módulo falha ou não existe (só append); `tests/backup/test_zip_data.py` — zip contém o `.sqlite` de fixture e extrai bit-a-bit igual.

Nesta ordem esse teste é `test_reg_dia_001`. Se o caminho antigo do plano divergir do contrato já mergulhado em `main`, vale o contrato e o esquema, como está nas notas.

## Dependências

Têm de estar fundidos em `main` antes de se implementar:

- PLN-01

## Ficheiros que este PR pode criar

- `engine/diario/__init__.py`
- `engine/diario/escrever.py` — só INSERT
- `engine/diario/ler.py` — leitura paginada
- `engine/biblioteca/etiquetas.py`
- `engine/biblioteca/filtrar.py` — etiquetas + tipo manual
- `engine/backup/zip_data.py`
- `apps/ui/src/components/biblioteca/Etiquetas.tsx`
- `apps/ui/src/components/biblioteca/ListaVirtualizada.tsx`
- `apps/ui/src/components/backup/CopiaSeguranca.tsx`
- `tests/diario/test_append.py`
- `tests/biblioteca/test_etiquetas.py`
- `tests/backup/test_zip_data.py`

Também os ficheiros de teste nomeados na secção de regressão, quando o plano ainda os não listava um a um.

## Não tocar

- contas, rede de sync, edição do diário, backup remoto
- apps/ui/src/components/chrome/, barra/, leque/, leitor/
- a lógica de SHA-256 desactualizado, que é PLN-02: a lista só mostra o estado

- `docs/verificacao/cobertura.md`, que é do fecho
- `tests/regressao/test_suite.py`, `tests/regressao/apoio.py`, `tests/regressao/exigir_agora.py` e `scripts/regressao.sh`
- `docs/origem/plano.md`
- `data/`, `models/`, pesos `.gguf`, `.onnx`, `.safetensors`, `.pt`, `.pth`

Excepção partilhada: acrescentar linhas no fim de `tests/regressao/manifesto.txt`. Não apagar, não reordenar, não repetir.

## Notas para não reabrir o âmbito

Diário só INSERT. Etiquetas manuais. tipo sugerido não escreve por cima do tipo manual. Backup é zip local de data/, sem upload. HTTP-library-list, HTTP-library-ingest, HTTP-library-tags e HTTP-backup. A UI da lista virtualizada usa o chrome de PLN-13; se esse PR ainda não estiver fundido, implementar primeiro o motor e rebasear antes dos componentes.

## Requisitos que este PR fecha

- `REQ-BIB-001` fecha com `REG-BIB-001`.
- `REQ-BIB-002` fecha com `REG-BIB-002`.
- `REQ-BIB-003` fecha com `REG-BIB-003`.
- `REQ-DIA-001` fecha com `REG-DIA-001`.
- `REQ-DIA-002` fecha com `REG-DIA-002`.
- `REQ-BAK-001` fecha com `REG-BAK-001`.
- `REQ-BAK-002` fecha com `REG-BAK-002`.
- `REQ-SEG-005` fecha com `REG-SEG-005`.
- `REQ-DES-002` fecha com `REG-DES-002`.

## Testes de regressão

Acrescentar no fim de `tests/regressao/manifesto.txt`, e só no fim:

- `tests/biblioteca/test_etiquetas.py::test_reg_bib_001`
  - Dado um documento, quando se lhe atribuem etiquetas, então ficam persistidas. Dado um filtro por uma delas, então só aparecem os documentos que a têm.
- `tests/biblioteca/test_etiquetas.py::test_reg_bib_002`
  - Dado um filtro por tipo, quando se aplica, então vale a escolha manual. Dado uma sugestão de tipo por embedding não confirmada, então não substitui o tipo manual.
- `apps/ui/src/components/biblioteca/reg-bib-003.test.tsx`
  - Dado milhares de documentos sintéticos, quando a lista abre, então o número de nós montados é uma janela e não o total.
- `tests/diario/test_append.py::test_reg_dia_001`
  - Dado uma procura, uma abertura de documento, um feedback e um fecho de dossier, quando cada acção completa, então o diário ganha uma entrada correspondente, por esta ordem. Não há operação que altere ou apague uma entrada antiga.
- `tests/diario/test_append.py::test_reg_dia_002`
  - Dado o diário a ser escrito, quando se observa rede e identidade, então não há login, conta remota nem envio do diário.
- `tests/backup/test_zip_data.py::test_reg_bak_001`
  - Dado um directório data de teste com um sqlite, quando se pede a cópia para um destino escolhido, então o zip contém esse sqlite e a extracção coincide bit a bit.
- `tests/backup/test_zip_data.py::test_reg_bak_002`
  - Dado a cópia de segurança, quando corre, então o destino é um caminho local e o módulo não faz upload.
- `tests/backup/test_zip_data.py::test_reg_seg_005`
  - Dado diário, SQLite e backup sem serviços externos, quando se usam, então esses módulos não abrem um cliente HTTP de upload.
- `apps/ui/src/components/biblioteca/reg-des-002.test.tsx`
  - Dado milhares de linhas, quando se faz scroll na biblioteca, então o número de nós montados permanece limitado e a lista não monta todas as linhas.

Um teste de UI é o caminho do ficheiro `.test.tsx`, que já contém o `reg` no nome. Um teste de motor é o node id `caminho::test_reg_…`.

## Definição de pronto

- [ ] O comportamento acima está implementado dentro da fronteira.
- [ ] `scripts/regressao.sh` está verde.
- [ ] O manifesto cresceu exactamente com os identificadores desta ordem.
- [ ] Não há ficheiros de pesos no git.
- [ ] O texto visível vem de `docs/interface/copy.md`, sem frase inventada para o mesmo estado.

## Paralelo

O motor pode avançar ao lado da onda 1 e dos planos que não usem diário, biblioteca nem backup. A UI da lista espera pelo chrome de PLN-13 e não edita barra, leque nem leitor.
