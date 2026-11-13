"""Desenho das bounding boxes e do painel de informações no frame."""

import cv2

from src import config

FONTE = cv2.FONT_HERSHEY_SIMPLEX


def cor_do_status(status: str):
    return {
        "LIVRE": config.COR_LIVRE,
        "ATENCAO": config.COR_ATENCAO,
        "LOTADO": config.COR_LOTADO,
    }[status]


def desenhar_deteccoes(frame, deteccoes):
    for i, d in enumerate(deteccoes, start=1):
        cv2.rectangle(frame, (d.x1, d.y1), (d.x2, d.y2), config.COR_CAIXA, 2)

        rotulo = f"#{i} {d.classe} {d.confianca:.0%}"
        (larg, alt), _ = cv2.getTextSize(rotulo, FONTE, 0.5, 1)
        # Fundo preenchido atrás do texto para manter a leitura em qualquer cena.
        topo = max(d.y1 - alt - 8, 0)
        cv2.rectangle(frame, (d.x1, topo), (d.x1 + larg + 6, topo + alt + 8), config.COR_CAIXA, -1)
        cv2.putText(frame, rotulo, (d.x1 + 3, topo + alt + 3), FONTE, 0.5, config.COR_TEXTO, 1, cv2.LINE_AA)


def desenhar_painel(frame, stats):
    cor = cor_do_status(stats.status)

    # Painel semitransparente no canto superior esquerdo.
    sobreposicao = frame.copy()
    cv2.rectangle(sobreposicao, (10, 10), (290, 175), config.COR_PAINEL, -1)
    cv2.addWeighted(sobreposicao, 0.7, frame, 0.3, 0, frame)

    linhas = [
        f"Pessoas: {stats.atual} / {stats.capacidade}",
        f"Ocupacao: {stats.ocupacao:.0%}",
        f"Pico: {stats.maximo} | Media: {stats.media_pessoas:.1f}",
        f"Area ocupada: {stats.area_ocupada:.1f}%",
    ]
    # Em imagem única o FPS não faz sentido, então só aparece em vídeo/webcam.
    if stats.total_frames > 1:
        linhas.append(f"FPS: {stats.fps:.1f}")
    for i, texto in enumerate(linhas):
        cv2.putText(frame, texto, (20, 35 + i * 24), FONTE, 0.55, config.COR_TEXTO, 1, cv2.LINE_AA)

    # Barra de ocupação (limitada a 100% na largura).
    x0, y0, largura = 20, 155, 260
    preenchido = int(largura * min(stats.ocupacao, 1.0))
    cv2.rectangle(frame, (x0, y0), (x0 + largura, y0 + 12), (90, 90, 90), -1)
    cv2.rectangle(frame, (x0, y0), (x0 + preenchido, y0 + 12), cor, -1)

    # Selo de status no canto superior direito.
    (larg, alt), _ = cv2.getTextSize(stats.status, FONTE, 0.8, 2)
    x = frame.shape[1] - larg - 30
    cv2.rectangle(frame, (x - 10, 10), (x + larg + 10, 20 + alt + 10), cor, -1)
    cv2.putText(frame, stats.status, (x, 20 + alt), FONTE, 0.8, config.COR_TEXTO, 2, cv2.LINE_AA)
