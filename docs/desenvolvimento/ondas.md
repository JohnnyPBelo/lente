# Ondas de implementação

Cada onda só começa quando a anterior, nas dependências indicadas, tem os testes do plano a passar. Dentro da onda, os planos podem ir em ramos separados se não tocarem nos mesmos ficheiros.

## Onda 0 — armazenamento

- [PLN-01](../planos/PLN-01-esquema-sqlite-e-migracoes.md). Sem modelos, sem HTTP, sem FTS/vec para além do que o SQL 001 precisar como estrutura vazia.

Nada do resto grava estado antes disto.

## Onda 1 — entradas, ainda sem semântica

Dependem do PLN-01. Entre si, 03–05 dependem dos tipos e do registo do PLN-02.

- [PLN-02](../planos/PLN-02-texto-markdown-e-docx.md) texto, Markdown, docx, SHA-256.
- [PLN-03](../planos/PLN-03-pdf-com-texto-e-caixas.md) PDF com texto e caixas.
- [PLN-04](../planos/PLN-04-ocr-tesseract.md) imagem e PDF sem texto.
- [PLN-05](../planos/PLN-05-url-e-recusa-privados.md) URL e recusa de endereços privados.

## Onda 2 — encontrar e decidir

- [PLN-06](../planos/PLN-06-blocos-frases-e-embeddings.md) depois da onda 1 (precisa de texto e de frases).
- [PLN-07](../planos/PLN-07-fts5-e-cosseno-exacto.md) depois do PLN-01 e do PLN-06 (vectores para inserir).
- [PLN-08](../planos/PLN-08-juiz-onnx.md) pode começar com o PLN-06: só precisa de pares texto, não da UI.
- [PLN-10](../planos/PLN-10-escalonador.md) pode começar depois do PLN-01. A fila de um documento passa a ser usada pela ingestão assim que existir.

## Onda 3 — uma procura com prova

- [PLN-09](../planos/PLN-09-fusao-rrf-limiar-e-platt.md) depois de PLN-07 e PLN-08.
- [PLN-11](../planos/PLN-11-escritor-e2b-e-duas-portas.md) depois de PLN-08 e PLN-09. Sem E2B no disco, o mesmo módulo devolve excertos.
- [PLN-12](../planos/PLN-12-api-do-chat-http.md) depois de PLN-09, PLN-10 e PLN-11. Até lá, os testes de API usam doubles.

## Onda 4 — interface

O contrato HTTP já está escrito, por isso o chrome pode nascer com respostas falsas. Liga-se ao motor quando o PLN-12 existir.

- [PLN-13](../planos/PLN-13-chrome-da-interface.md) barra lateral, área de chat, vidro.
- [PLN-14](../planos/PLN-14-barra-de-modos-e-lentes.md) depois do PLN-13.
- [PLN-15](../planos/PLN-15-leque-e-leitor.md) depois do PLN-13. As rotas de documento entram no PLN-12 ou neste plano, como `engine/api/rotas_documento.py`.

## Onda 5 — o que distingue a Lente de um chat

Podem avançar em paralelo depois das dependências.

- [PLN-16](../planos/PLN-16-feedback-e-lora-do-juiz.md) depois do PLN-08. O treino só corre com o slot do PLN-10 livre.
- [PLN-17](../planos/PLN-17-importar-e-exportar-correcoes.md) depois do PLN-16.
- [PLN-18](../planos/PLN-18-dossier.md) depois do PLN-01 e de haver mensagens com citações (PLN-12).
- [PLN-19](../planos/PLN-19-alertas.md) depois de PLN-06 e PLN-08. Não chama o E2B.
- [PLN-20](../planos/PLN-20-diario-etiquetas-e-copia-de-seguranca.md) depois do PLN-01. A UI da biblioteca virtualizada pode esperar pelo PLN-13.

## Onda 6 — fecho

- [PLN-21](../planos/PLN-21-estados-vazios-a11y-e-comando-unico.md) por último. É aqui que `lente` sobe UI e motor num comando e que os estados vazios ficam ligados aos códigos de erro da API.

## Primeiro corte utilizável

Depois da onda 3 mais PLN-13, uma pessoa consegue indexar um `.txt`, procurar, e ver excertos no browser, ainda sem leque, dossier, alertas nem LoRA. Esse corte não substitui os planos seguintes: o produto descrito no plano de origem só fecha na onda 6.
