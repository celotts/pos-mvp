from core.crud_base import CRUDBase
from models.pos_terminal import PosTerminal
from schemas.pos_terminal import PosTerminalCreate, PosTerminalUpdate
from sqlalchemy.orm import selectinload


class CRUDPosTerminal(CRUDBase[PosTerminal, PosTerminalCreate, PosTerminalUpdate]):
    def __init__(self, model: type[PosTerminal]):
        super().__init__(model)
        self.default_loads = [selectinload(self.model.store)]


crud_pos_terminal = CRUDPosTerminal(PosTerminal)
