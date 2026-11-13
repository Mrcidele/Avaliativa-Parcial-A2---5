"""Cálculo e registro das métricas de ocupação."""

import csv
import time
from datetime import datetime
from pathlib import Path

from src import config


class Estatisticas:
    def __init__(self, capacidade: int):
        self.capacidade = capacidade
        self.total_frames = 0
        self.soma_pessoas = 0
        self.maximo = 0
        self.soma_confianca = 0.0
        self.total_deteccoes = 0
        self.atual = 0
        self.area_ocupada = 0.0  # % do frame coberto pelas caixas
        self.fps = 0.0
        self._ultimo_tempo = time.time()
        self.historico = []  # uma linha por frame, salva no CSV ao final

    def atualizar(self, deteccoes, largura_frame, altura_frame):
        agora = time.time()
        intervalo = agora - self._ultimo_tempo
        self._ultimo_tempo = agora
        if intervalo > 0:
            # Média móvel para o FPS não ficar oscilando na tela.
            self.fps = 0.9 * self.fps + 0.1 * (1 / intervalo) if self.fps else 1 / intervalo

        self.atual = len(deteccoes)
        self.total_frames += 1
        self.soma_pessoas += self.atual
        self.maximo = max(self.maximo, self.atual)
        self.total_deteccoes += self.atual
        self.soma_confianca += sum(d.confianca for d in deteccoes)

        area_frame = largura_frame * altura_frame
        self.area_ocupada = 100 * sum(d.area for d in deteccoes) / area_frame

        self.historico.append({
            "horario": datetime.now().strftime("%H:%M:%S"),
            "frame": self.total_frames,
            "pessoas": self.atual,
            "ocupacao_pct": round(self.ocupacao * 100, 1),
            "status": self.status,
            "confianca_media": round(self._media_conf(deteccoes), 3),
        })

    @staticmethod
    def _media_conf(deteccoes):
        return sum(d.confianca for d in deteccoes) / len(deteccoes) if deteccoes else 0.0

    @property
    def ocupacao(self) -> float:
        return self.atual / self.capacidade

    @property
    def status(self) -> str:
        if self.ocupacao >= config.LIMITE_LOTADO:
            return "LOTADO"
        if self.ocupacao >= config.LIMITE_ATENCAO:
            return "ATENCAO"
        return "LIVRE"

    @property
    def media_pessoas(self) -> float:
        return self.soma_pessoas / self.total_frames if self.total_frames else 0.0

    @property
    def confianca_media(self) -> float:
        return self.soma_confianca / self.total_deteccoes if self.total_deteccoes else 0.0

    def salvar_csv(self, pasta=config.PASTA_RESULTADOS) -> Path:
        Path(pasta).mkdir(exist_ok=True)
        caminho = Path(pasta) / f"ocupacao_{datetime.now():%Y%m%d_%H%M%S}.csv"
        with open(caminho, "w", newline="", encoding="utf-8") as f:
            escritor = csv.DictWriter(f, fieldnames=self.historico[0].keys())
            escritor.writeheader()
            escritor.writerows(self.historico)
        return caminho

    def resumo(self) -> str:
        return (
            "\n===== RESUMO DA SESSAO =====\n"
            f"Frames analisados : {self.total_frames}\n"
            f"Capacidade da sala: {self.capacidade} pessoas\n"
            f"Pico de ocupacao  : {self.maximo} pessoas "
            f"({self.maximo / self.capacidade:.0%})\n"
            f"Media de pessoas  : {self.media_pessoas:.1f}\n"
            f"Confianca media   : {self.confianca_media:.0%}\n"
            "============================"
        )
