# Estados vazios

Origem: `docs/origem/plano.md` — «Interface» (lista exacta). Requisito: `REQ-VAZ-001`.

Cada estado tem superfície dedicada — **não** uma lista ou fio em branco sem explicação. Copy canónica em [copy.md](copy.md).

## Lista do plano (exacta)

| # | Estado | Quando aparece | O que o utilizador vê |
| --- | --- | --- | --- |
| 1 | **Biblioteca sem ficheiros** | Biblioteca aberta e vazia | Estado vazio dedicado a importar / acrescentar documentos — não uma grelha vazia muda |
| 2 | **Modelo a descarregar** | Download de pesos em curso (ou licença HF a bloquear) | Indicação observável de descarregar; se a licença bloquear, a app abre e **diz onde pôr o ficheiro** |
| 3 | **Prosa toda filtrada** | Nenhuma frase passou as duas portas | Excertos e miniaturas **ou** só aviso — **sem** prosa fantasma; miniaturas podem ter vindo primeiro |
| 4 | **Página sem texto** | Documento/página sem texto extraível útil | Aviso de página sem texto (OCR falhou ou imagem sem camada de texto) |
| 5 | **URL recusada** | Ingestão de URL privada ou recusada | Estado «URL recusada» com razão clara |
| 6 | **Conversa nova** | Conversa sem mensagens | Estado pronto para a primeira procura — **não** um erro |
| 7 | **Procura sem documentos** | Nada acima do limiar do juiz | Aviso de que não há nada acima do limiar; **sem** miniaturas a fingir hits |

## Regras transversais

- Idioma: português de Portugal.
- Sem ilustrações obrigatórias; texto e hierarquia bastam.
- «Prosa toda filtrada» ≠ «Procura sem documentos»: o primeiro pode ainda ter trechos/miniaturas; o segundo não mostra documentos.
- Sem E2B: o chat segue com excertos e miniaturas quando existirem candidatos — alinhado ao plano «Como corre».

## Fora desta lista

Estados de erro genéricos de rede (a app é local), spinners de indexação de um ficheiro concreto (podem coexistir, mas não substituem os sete acima).
