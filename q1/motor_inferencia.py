import json
from pathlib import Path

class MotorInferencia:
    def __init__(self, caminho_base="knowledge_base.json", explicador=None):
        # Carregando a estrutura exata do JSON
        caminho = Path(caminho_base)
        if not caminho.is_absolute():
            caminho = (Path(__file__).resolve().parent / caminho).resolve()
        with open(caminho, 'r', encoding='utf-8') as f:
            self.base = json.load(f)
        self.explicador = explicador
        if explicador is not None:
            explicador._motor = self
        
        self.regras = self.base.get("rules", {}).get("items", [])
        self.hipoteses = self.base.get("hypotheses", {}).get("items", [])
        
        # Estado da sessão em tempo de execução
        self.sessao = {
            "session_id": "sess_001",
            "strategy": "hybrid",
            "facts_confirmed": set(),
            "facts_denied": set(),
            "facts_unknown": set(),
            "facts_inferred": set(),
            "rules_fired": set(),
            "rules_fired_chronological": [], # NOVA LISTA para rastreamento ordenado
            "hypotheses_confirmed": set(),
            "current_goal": None,
            "questions_asked": set()
        }

    def _condicoes_satisfeitas(self, condicoes):
        # Verifica se todos os fatos da premissa estão confirmados ou inferidos
        fatos_conhecidos = self.sessao["facts_confirmed"].union(self.sessao["facts_inferred"])
        return all(cond in fatos_conhecidos for cond in condicoes)

    def encadeamento_para_frente(self):
        # Forward Chaining: dispara regras guiado pelos dados
        novos_fatos = True
        while novos_fatos:
            novos_fatos = False
            for regra in self.regras:
                id_regra = regra["id"]
                if id_regra not in self.sessao["rules_fired"]:
                    if self._condicoes_satisfeitas(regra["conditions"]):
                        self.sessao["rules_fired"].add(id_regra)
                        if id_regra not in self.sessao["rules_fired_chronological"]:
                            self.sessao["rules_fired_chronological"].append(id_regra)
                        conclusao = regra["conclusion"]
                        
                        # Adiciona à lista correspondente (fato inferido ou hipótese final)
                        if "fact_id" in conclusao:
                            self.sessao["facts_inferred"].add(conclusao["fact_id"])
                        elif "hypothesis_id" in conclusao:
                            self.sessao["hypotheses_confirmed"].add(conclusao["hypothesis_id"])
                        
                        novos_fatos = True

    def encadeamento_para_tras(self, objetivo_id):
        # Backward Chaining: guiado por objetivos/hipóteses
        self.sessao["current_goal"] = objetivo_id
        
        # Busca regras que concluem este objetivo
        regras_objetivo = [r for r in self.regras if r["conclusion"].get("hypothesis_id") == objetivo_id or r["conclusion"].get("fact_id") == objetivo_id]
        
        for regra in regras_objetivo:
            todas_condicoes_ok = True
            for condicao in regra["conditions"]:
                if condicao in self.sessao["facts_denied"]:
                    todas_condicoes_ok = False
                    break
                
                if condicao not in self.sessao["facts_confirmed"] and condicao not in self.sessao["facts_inferred"]:
                    # Se não sabemos o fato, verificamos se ele é inferível por outra regra
                    sub_regras = [r for r in self.regras if r["conclusion"].get("fact_id") == condicao]
                    if sub_regras:
                        if not self.encadeamento_para_tras(condicao):
                            todas_condicoes_ok = False
                            break
                    else:
                        # É um fato que precisa vir de um input externo (interface)
                        self.sessao["questions_asked"].add(condicao)
                        todas_condicoes_ok = False 
                        
            if todas_condicoes_ok:
                self.sessao["rules_fired"].add(regra["id"])
                if "fact_id" in regra["conclusion"]:
                    self.sessao["facts_inferred"].add(regra["conclusion"]["fact_id"])
                elif "hypothesis_id" in regra["conclusion"]:
                    self.sessao["hypotheses_confirmed"].add(regra["conclusion"]["hypothesis_id"])
                return True
        return False

    def encadeamento_hibrido(self, objetivo_principal):
        # Híbrido: Roda o forward com o que tem, depois tenta provar o objetivo com backward
        self.encadeamento_para_frente()
        if objetivo_principal not in self.sessao["hypotheses_confirmed"]:
            self.encadeamento_para_tras(objetivo_principal)