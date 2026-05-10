# ONBot — Discord Role Monitor

Bot para o servidor **Clan ON** que monitora promoções e rebaixamentos de cargos e envia avisos automáticos no canal configurado.

## Funcionalidades

- Detecta quando um membro **ganha** um cargo monitorado e envia:
  > 🚀 Promoção Detectada! O membro @membro agora possui o cargo **nome do cargo**! Parabéns! 🎊

- Detecta quando um membro **perde** um cargo monitorado e envia:
  > 📉 Rebaixamento Detectado! O membro @membro perdeu o cargo **nome do cargo**! 😔

- Exclusivo para o servidor configurado — ignora eventos de outros servidores.

## Cargos monitorados

| Cargo | ID |
|---|---|
| OWNER | 1500321124267987075 |
| SUB OWNER | 1500357136490692658 |
| CEO | 1500322498972221603 |
| ADMIN | 1500322585718820894 |
| MODERADOR | 1500327641532731594 |
| AJUDANTE | 1500322742761820250 |
| APRENDIZ | 1500322873389220052 |
| Líder de Divisão | 1500322989085032479 |
| Sub Líder De Divisão | 1500323156316000278 |
| STAFF ADM | 1500322650378076291 |
| STAFF | 1500325328432791713 |
| MEMBRO | 1500323900754493551 |
| DIV1 | 1500324171337568256 |
| DIV2 | 1500324377609375844 |
| DIV3 | 1500324425432698890 |
| PVP | 1500324715087003721 |
| BUILDER | 1500324848340308029 |
| MINERADOR | 1500325078754132080 |

## Configuração

### Variáveis de ambiente

| Variável | Descrição |
|---|---|
| `TOKEN` | Token do bot obtido no Discord Developer Portal |

### Requisitos

- Python 3.11+
- `discord.py==2.7.1`

```bash
pip install -r requirements.txt
python bot.py
```

### Intents necessárias

No [Discord Developer Portal](https://discord.com/developers/applications), ative em **Bot → Privileged Gateway Intents**:
- ✅ Server Members Intent

## Hospedagem no Discloud

O arquivo `discloud.config` já está configurado. Basta fazer upload do projeto no [Discloud](https://discloudbot.com).

## Estrutura

```
discord-bot/
├── bot.py            # Código principal do bot
├── discloud.config   # Configuração de hospedagem (Discloud)
├── requirements.txt  # Dependências Python
└── README.md         # Este arquivo
```
