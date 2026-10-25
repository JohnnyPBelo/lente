# Ordem de trabalho PLN-05

Fonte: `docs/planos/PLN-05-url-e-recusa-privados.md`. Este ramo não implementa a aplicação. A implementação entra depois, no mesmo pull request, quando as dependências estiverem fundidas e os caminhos de **Não tocar** forem respeitados.

## Objectivo

Importar artigo via URL HTTP(S): descarregar, extrair texto principal, registar como documento; **recusar** endereços privados, loopback, link-local e esquemas não HTTP(S).

## Fronteira

o que NÃO entra neste plano — browser automation, login em sites, sync cloud, PDF remoto complexo além do fluxo já coberto por extractores; UI do estado «URL recusada» (copy em PLN-21).

## Teste que falha primeiro, no plano

`tests/ingestao/test_ssrf.py` — `validar_url("http://127.0.0.1/x")` e `http://192.168.0.1/`, `http://10.0.0.1/`, `http://[::1]/`, `file:///etc/passwd` levantam `UrlRecusada`; um host público de teste (mock DNS/IP) passa a validação estática.

Nesta ordem esse teste é `test_reg_seg_001`. Se o caminho antigo do plano divergir do contrato já mergulhado em `main`, vale o contrato e o esquema, como está nas notas.

## Dependências

Têm de estar fundidos em `main` antes de se implementar:

- PLN-01
- PLN-02

## Ficheiros que este PR pode criar

- `engine/ingestao/url.py` — fetch + extracção
- `engine/ingestao/ssrf.py` — validação de host/IP (bloqueio privado)
- `tests/ingestao/test_ssrf.py`
- `tests/ingestao/test_url.py`

Também os ficheiros de teste nomeados na secção de regressão, quando o plano ainda os não listava um a um.

## Não tocar

- engine/ingestao/pdf.py, ocr.py, texto.py, markdown.py, docx.py
- apps/ui/ e o estado vazio visível, que é PLN-21
- engine/resposta/, engine/api/

- `docs/verificacao/cobertura.md`, que é do fecho
- `tests/regressao/test_suite.py`, `tests/regressao/apoio.py`, `tests/regressao/exigir_agora.py` e `scripts/regressao.sh`
- `docs/origem/plano.md`
- `data/`, `models/`, pesos `.gguf`, `.onnx`, `.safetensors`, `.pt`, `.pth`

Excepção partilhada: acrescentar linhas no fim de `tests/regressao/manifesto.txt`. Não apagar, não reordenar, não repetir.

## Notas para não reabrir o âmbito

O valor HTTP de erro é url_privada, como em docs/estrutura/contrato-http.md. A excepção pode chamar-se UrlRecusada. O título visível «URL recusada» é copy de PLN-21. User-Agent identificável Lente, timeout e limite de tamanho. Sem login e sem rede persistente.

## Requisitos que este PR fecha

- `REQ-ING-007` fecha com `REG-ING-007`.
- `REQ-SEG-001` fecha com `REG-SEG-001`.

## Testes de regressão

Acrescentar no fim de `tests/regressao/manifesto.txt`, e só no fim:

- `tests/ingestao/test_url.py::test_reg_ing_007`
  - Dado um URL HTTP(S) cujo DNS e o corpo são simulados como públicos, quando se submete, então o texto entra como documento. Dado um endereço recusado, então o código estável entregue à API é url_privada, como no contrato HTTP. A matriz de IPs e de redirects fica em REG-SEG-001.
- `tests/ingestao/test_ssrf.py::test_reg_seg_001`
  - Dado http://127.0.0.1/x, http://10.0.0.1/, http://192.168.0.1/, http://169.254.169.254/, http://[::1]/, file:///etc/passwd e um redirect que cai num IP privado, quando se valida, então levanta UrlRecusada e não há nenhum fetch para esses alvos. Dado um host cujo mock resolve só para um IP público, então a validação estática passa.

Um teste de UI é o caminho do ficheiro `.test.tsx`, que já contém o `reg` no nome. Um teste de motor é o node id `caminho::test_reg_…`.

## Definição de pronto

- [ ] O comportamento acima está implementado dentro da fronteira.
- [ ] `scripts/regressao.sh` está verde.
- [ ] O manifesto cresceu exactamente com os identificadores desta ordem.
- [ ] Não há ficheiros de pesos no git.
- [ ] Este PR não introduz copy de interface.

## Paralelo

Pode avançar ao lado de PLN-03, de PLN-04 e de PLN-10. Não cria extractores de PDF, OCR ou docx.
