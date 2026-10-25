# Regressão acumulada

A suite cresce. Não se apaga, não se salta e não se mete de lado um teste que já entrou no manifesto. Um teste vermelho corrige-se, ou o comportamento que ele protege é reposto.

## Antes de integrar código em `main`

`scripts/regressao.sh`, a partir da raiz, tem de terminar verde. O GitHub Actions corre esse script em cada pull request e em cada push para `main` (workflow `Regressão`, job `regressao`). Não há segredos nem descarga de modelos.

Um gancho local é opcional e não substitui o Actions. O ficheiro `scripts/githooks/pre-push` chama o mesmo script. Quem o quiser no seu clone activa-o à mão:

```bash
git config core.hooksPath scripts/githooks
```

Este repositório não define `core.hooksPath`. A porta que impede integração é o workflow.

O ramo `main` exige o check `regressao`, com o ramo actualizado face a `main` (`strict`). O comando que define essa protecção é:

```bash
gh api -X PUT repos/JohnnyPBelo/lente/branches/main/protection \
  --input - <<'EOF'
{
  "required_status_checks": {
    "strict": true,
    "contexts": ["regressao"]
  },
  "enforce_admins": false,
  "required_pull_request_reviews": null,
  "restrictions": null
}
EOF
```

O nome do check é o nome do job, `regressao`.

## O que o script faz

1. Confirma Python 3.11 ou superior. Se o `pytest` não estiver instalado, sai com erro e a mensagem para o instalar (`python3 -m pip install pytest`). Não o instala sozinho.
2. Lê `tests/regressao/manifesto.txt`.
3. Corre o pytest só sobre os node ids dessa lista.
4. Se mais tarde existir `apps/ui` e o manifesto tiver caminhos Vitest (linhas sem `::`), corre esses ficheiros. Enquanto `apps/ui` não existir, uma linha dessas faz falhar a suite.
5. Falha se algum identificador marcado `agora` em `docs/verificacao/cobertura.md` não estiver coberto pelo manifesto.

Não cria `data/` nem `models/`, não descarrega pesos e não escuta num porto. `PYTHONDONTWRITEBYTECODE=1` e o pytest sem cache para o directório de trabalho ficar limpo.

## Manifesto

`tests/regressao/manifesto.txt` é só de acrescentar. Cada linha é um node id do pytest (`caminho/test_ficheiro.py::test_nome`) ou, quando a interface existir, um caminho Vitest desde a raiz (`apps/ui/…/reg-cht-001.test.tsx`).

Linhas em branco ignoram-se. Comentários não são aceites.

Um teste falha quando:

- o manifesto fica mais curto, ou as linhas antigas deixam de ser o prefixo, face ao ficheiro já commitado (e, num pull request, face à base);
- uma linha está repetida;
- um node id não é uma função recolhida pelo pytest.

No Actions, a variável `REGRESSAO_BASE_SHA` é o commit de base do pull request, ou o commit anterior no push para `main`.

Um pull request de código acrescenta linhas no fim. Não apaga, não reordena e não comenta um teste para ele deixar de correr. Quarentena não existe.

Um pull request só de especificação também corre a suite, e ela tem de continuar verde. Não é obrigado a acrescentar linhas se não muda comportamento.

O nome estável de uma regressão de requisito é o do requisito com o prefixo `REG`. No pytest a função chama-se `test_reg_ing_001` para `REG-ING-001` (minúsculas e `_` no lugar de `-`). No Vitest o caminho contém `reg-ing-001`. O estado `agora` exige que o manifesto tenha `reg_ing_001` ou `reg-ing-001`.

## Esquemas JSON

Os exemplos em `docs/dados/exemplos/*.json` têm de ser aceites pelo esquema irmão em `docs/dados/` (`dossier.exemplo.json` → `dossier.schema.json`). O verificador é da biblioteca padrão e cobre só o que os esquemas actuais usam: `type`, `required`, `properties`, `additionalProperties`, `items`, `const`, `enum`, `pattern`, `minLength`, `minimum`, `minItems` e `format: date-time` em ISO-8601 com `Z` ou desvio horário. Não valida o dialecto JSON Schema inteiro e não depende do pacote `jsonschema`.

## O que já corre

Os oito testes do manifesto actual não implementam a aplicação. Protegem o arnês, os exemplos, a tabela de cobertura, a ausência de pesos versionados (`.gguf`, `.onnx`, `.safetensors`, `.pt`, `.pth`) e a frase da secção Buracos em `docs/rastreio/matriz.md`, que continua a dizer que não há buracos. `docs/origem/plano.md` tem de continuar no repositório.
