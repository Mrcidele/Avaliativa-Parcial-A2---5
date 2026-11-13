# Monitor de Ocupação de Salas — YOLO + OpenCV

Aplicação em Python que detecta pessoas em imagem, vídeo ou webcam com um modelo
YOLOv8 pré-treinado, compara a quantidade com a capacidade da sala e mostra em
tempo real o status **LIVRE / ATENCAO / LOTADO**, além de estatísticas da sessão.

## Requisitos

- Python 3.10 ou superior
- Webcam (opcional, para o modo em tempo real)

## Instalação

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux / macOS
source venv/bin/activate

pip install -r requirements.txt
```

Na primeira execução o arquivo de pesos `yolov8n.pt` (~6 MB) é baixado automaticamente.

## Como executar

```bash
# Webcam (padrão)
python main.py

# Webcam com capacidade de 5 pessoas
python main.py --capacidade 5

# Imagem de exemplo, salvando o resultado
python main.py --fonte amostras/bus.jpg --capacidade 4 --salvar

# Arquivo de vídeo
python main.py --fonte meu_video.mp4 --salvar
```

Durante a execução em vídeo/webcam:

| Tecla | Ação                |
|-------|---------------------|
| `Q`   | encerra o programa  |
| `S`   | salva um print      |

### Parâmetros

| Parâmetro                | Padrão       | Descrição                                       |
|--------------------------|--------------|-------------------------------------------------|
| `--fonte`                | `0`          | `0` = webcam, ou caminho de imagem/vídeo        |
| `--capacidade`           | `10`         | capacidade máxima da sala                       |
| `--confianca`            | `0.40`       | confiança mínima para aceitar uma detecção      |
| `--modelo`               | `yolov8n.pt` | pesos YOLO (ex.: `yolov8s.pt` para mais precisão) |
| `--sem-preprocessamento` | —            | desativa a equalização de contraste (CLAHE)     |
| `--salvar`               | —            | salva a imagem/vídeo processado em `resultados/` |
| `--sem-janela`           | —            | processa sem abrir janela                       |

## Saídas

Tudo fica na pasta `resultados/`:

- `resultado_*.jpg` / `resultado_*.mp4` — imagem ou vídeo com as caixas e o painel
- `ocupacao_*.csv` — histórico por frame (horário, pessoas, % de ocupação, status, confiança média)

Ao fechar, o terminal mostra um resumo com pico, média de pessoas e confiança média.

## Estrutura

```
monitor-ocupacao/
├── main.py              # ponto de entrada: argumentos e laço de captura
├── requirements.txt
├── relatorio/           # relatório técnico (.docx)
├── amostras/            # imagens de teste
├── resultados/          # saídas geradas
└── src/
    ├── config.py        # constantes (modelo, cores, limites de ocupação)
    ├── detector.py      # pré-processamento + detecção com YOLO
    ├── estatisticas.py  # métricas, status e exportação CSV
    └── visualizacao.py  # bounding boxes e painel na tela
```
