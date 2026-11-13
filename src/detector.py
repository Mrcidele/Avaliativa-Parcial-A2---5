"""Detecção de pessoas com YOLO."""

from dataclasses import dataclass

import cv2
from ultralytics import YOLO

from src import config


@dataclass
class Deteccao:
    """Um objeto detectado em um frame."""
    x1: int
    y1: int
    x2: int
    y2: int
    classe: str
    confianca: float

    @property
    def area(self) -> int:
        return (self.x2 - self.x1) * (self.y2 - self.y1)


class DetectorPessoas:
    def __init__(self, modelo=config.MODELO_PADRAO, confianca=config.CONFIANCA_MINIMA):
        # Na primeira execução o ultralytics baixa os pesos automaticamente.
        self.modelo = YOLO(modelo)
        self.confianca = confianca

    @staticmethod
    def preprocessar(frame):
        """Equaliza o contraste no canal de luminância (CLAHE).

        Ajuda em salas mal iluminadas sem alterar as cores, que o modelo
        também usa para reconhecer as pessoas.
        """
        lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        l = clahe.apply(l)
        return cv2.cvtColor(cv2.merge((l, a, b)), cv2.COLOR_LAB2BGR)

    def detectar(self, frame, preprocessar=True) -> list[Deteccao]:
        entrada = self.preprocessar(frame) if preprocessar else frame

        # classes=[0] faz o YOLO retornar apenas pessoas.
        resultado = self.modelo.predict(
            entrada,
            conf=self.confianca,
            classes=[config.CLASSE_PESSOA],
            verbose=False,
        )[0]

        deteccoes = []
        for caixa in resultado.boxes:
            x1, y1, x2, y2 = map(int, caixa.xyxy[0].tolist())
            id_classe = int(caixa.cls[0])
            deteccoes.append(Deteccao(
                x1, y1, x2, y2,
                classe=self.modelo.names[id_classe],
                confianca=float(caixa.conf[0]),
            ))
        return deteccoes
