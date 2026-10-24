# Acessibilidade — `REQ-A11`

## REQ-A11-001

**Enunciado:** Com `prefers-reduced-motion: reduce`, o movimento é encurtado sem remover o leque nem o leitor.

**Origem:** docs/origem/plano.md — «O chat e o leitor»

**Critérios de aceitação:**

1. **Dado** o sistema com `prefers-reduced-motion: reduce`, **quando** o utilizador percorre mensagem → leque → leitor → recolher, **então** as animações são reduzidas/encurtadas e o leque e o leitor continuam disponíveis e utilizáveis.

**Não pede:** desactivar todas as transições CSS da app; modo alto contraste completo neste requisito.

---

## REQ-A11-002

**Enunciado:** O menu de modos da barra é operável por teclado: `+` ou `/` abrem; setas escolhem; Enter confirma; Escape regressa à procura normal.

**Origem:** docs/origem/plano.md — «A barra de escrita»

**Critérios de aceitação:**

1. **Dado** o foco na barra, **quando** o utilizador usa apenas teclado (`+` ou `/`, setas, Enter, Escape), **então** consegue abrir o menu, escolher um modo, confirmá-lo e voltar ao modo Procurar sem rato.

**Não pede:** conformidade WCAG 2.2 AA completa documentada; leitores de ecrã com scripts ARIA avançados além do operável por teclado deste menu.
