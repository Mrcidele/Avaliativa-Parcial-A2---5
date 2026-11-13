"""Sistema de Monitoramento de Ocupação de Salas com YOLO + OpenCV.

Exemplos:
    python main.py                               # webcam
    python main.py --fonte amostras/bus.jpg      # imagem
    python main.py --fonte video.mp4 --salvar    # vídeo, salvando o resultado
"""

import argparse
from datetime import datetime
from pathlib import Path

import cv2

from src import config
from src.detector import DetectorPessoas
from src.estatisticas import Estatisticas
from src.visualizacao import desenhar_deteccoes, desenhar_painel

EXTENSOES_IMAGEM = {".jpg", ".jpeg", ".png", ".bmp"}


def ler_argumentos():
    p = argparse.ArgumentParser(description="Monitoramento de ocupação de salas com YOLO")
    p.add_argument("--fonte", default="0", help="0 = webcam, ou caminho de imagem/vídeo")
    p.add_argument("--capacidade", type=int, default=config.CAPACIDADE_PADRAO)
    p.add_argument("--confianca", type=float, default=config.CONFIANCA_MINIMA)
    p.add_argument("--modelo", default=config.MODELO_PADRAO)
    p.add_argument("--sem-preprocessamento", action="store_true", help="desativa o CLAHE")
    p.add_argument("--salvar", action="store_true", help="salva a imagem/vídeo processado")
    p.add_argument("--sem-janela", action="store_true", help="não abre janela (útil em servidor)")
    return p.parse_args()


def processar_frame(frame, detector, stats, preprocessar):
    deteccoes = detector.detectar(frame, preprocessar)
    altura, largura = frame.shape[:2]
    stats.atualizar(deteccoes, largura, altura)
    desenhar_deteccoes(frame, deteccoes)
    desenhar_painel(frame, stats)
    return frame


def caminho_saida(sufixo):
    Path(config.PASTA_RESULTADOS).mkdir(exist_ok=True)
    return str(Path(config.PASTA_RESULTADOS) / f"resultado_{datetime.now():%Y%m%d_%H%M%S}{sufixo}")


def rodar_imagem(args, detector, stats):
    frame = cv2.imread(args.fonte)
    if frame is None:
        raise SystemExit(f"Não foi possível abrir a imagem: {args.fonte}")

    frame = processar_frame(frame, detector, stats, not args.sem_preprocessamento)

    if args.salvar:
        destino = caminho_saida(".jpg")
        cv2.imwrite(destino, frame)
        print(f"Imagem salva em {destino}")
    if not args.sem_janela:
        cv2.imshow("Monitor de Ocupacao", frame)
        cv2.waitKey(0)


def rodar_video(args, detector, stats):
    # "0" vira o índice inteiro da webcam; qualquer outra coisa é um arquivo.
    fonte = int(args.fonte) if args.fonte.isdigit() else args.fonte
    captura = cv2.VideoCapture(fonte)
    if not captura.isOpened():
        raise SystemExit(f"Não foi possível abrir a fonte: {args.fonte}")

    gravador = None
    if args.salvar:
        fps = captura.get(cv2.CAP_PROP_FPS) or 20
        largura = int(captura.get(cv2.CAP_PROP_FRAME_WIDTH))
        altura = int(captura.get(cv2.CAP_PROP_FRAME_HEIGHT))
        destino = caminho_saida(".mp4")
        gravador = cv2.VideoWriter(destino, cv2.VideoWriter_fourcc(*"mp4v"), fps, (largura, altura))

    print("Pressione Q para sair e S para salvar um print.")
    while True:
        ok, frame = captura.read()
        if not ok:
            break  # fim do vídeo ou webcam desconectada

        frame = processar_frame(frame, detector, stats, not args.sem_preprocessamento)

        if gravador:
            gravador.write(frame)
        if not args.sem_janela:
            cv2.imshow("Monitor de Ocupacao", frame)
            tecla = cv2.waitKey(1) & 0xFF
            if tecla == ord("q"):
                break
            if tecla == ord("s"):
                destino = caminho_saida(".jpg")
                cv2.imwrite(destino, frame)
                print(f"Print salvo em {destino}")

    captura.release()
    if gravador:
        gravador.release()
        print(f"Vídeo salvo em {destino}")


def main():
    args = ler_argumentos()
    detector = DetectorPessoas(args.modelo, args.confianca)
    stats = Estatisticas(args.capacidade)

    if Path(args.fonte).suffix.lower() in EXTENSOES_IMAGEM:
        rodar_imagem(args, detector, stats)
    else:
        rodar_video(args, detector, stats)

    cv2.destroyAllWindows()

    if stats.total_frames:
        print(stats.resumo())
        print(f"Histórico salvo em {stats.salvar_csv()}")


if __name__ == "__main__":
    main()
