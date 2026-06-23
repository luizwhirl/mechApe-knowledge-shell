# Base de Conhecimento: Diagnóstico de Erros e Performance em Jogos de PC

**Domínio:** Suporte técnico focado estritamente em problemas de execução, travamentos e desempenho em jogos de PC.

---

## 1. Fatos Possíveis (Mínimo de 30)

Estes são os "sintomas", alertas ou condições observáveis que o usuário poderá responder ou que o sistema irá deduzir durante a consulta.

**Desempenho e Execução:**
1. O jogo fecha sozinho para a área de trabalho (Crash).
2. Ocorre queda brusca de FPS (Stuttering) durante o jogo.
3. O jogo apresenta artefatos visuais na tela (cores estranhas, polígonos esticados).
4. O jogo abre em segundo plano, mas não exibe imagem.
5. Os tempos de carregamento (Loading) estão excessivamente longos.
6. O erro ocorre imediatamente ao tentar abrir o jogo.
7. O erro ocorre apenas após algumas horas de gameplay.
8. O áudio do jogo apresenta estalos, atrasos ou falhas.
9. A tela congela, mas o som do jogo continua rodando.

**Launchers e Contas (Steam / Rockstar / Epic / etc):**
10. O erro ocorre ao tentar iniciar pelo launcher da Steam.
11. A conta da Rockstar Games foi vinculada à Steam.
12. Ocorre falha de "Social Club failed to initialize".
13. Ocorre erro de autenticação de conta de terceiros.
14. A sincronização de arquivos na nuvem da Steam falhou.
15. O cliente do jogo não foi atualizado recentemente.

**Software e Sistema Operacional:**
16. Uma mensagem de "Arquivo DLL ausente" ou "Corrompido" é exibida.
17. Ocorreu uma tela azul (BSOD) durante a execução.
18. O Windows foi atualizado nos últimos 3 dias.
19. O driver de vídeo (GPU) não é atualizado há mais de 6 meses.
20. Há uma notificação de falha de "Permissão de Administrador".
21. O antivírus ou Windows Defender bloqueou o executável do jogo.
22. Existem modificações não oficiais (Mods) instaladas no diretório do jogo.

**Overlays (Sobreposições de Tela):**
23. O overlay (sobreposição) do Discord está ativado.
24. O overlay da Steam está ativado.
25. O overlay do GeForce Experience / AMD Adrenalin está ativado.
26. O software Rivatuner ou MSI Afterburner está rodando em segundo plano.

**Hardware e Ambiente:**
27. A temperatura da CPU atinge mais de 85°C.
28. A temperatura da GPU atinge mais de 85°C.
29. O uso da memória RAM chega a mais de 95% durante a execução.
30. O uso do disco (HD/SSD) fica em 100% constante.
31. O jogo está instalado em um disco rígido mecânico (HDD) antigo.

---

## 2. Hipóteses / Diagnósticos (Mínimo de 5)

Estas são as conclusões finais que o motor de inferência tentará provar para entregar o diagnóstico ao usuário.

* **H1:** Conflito de overlay (sobreposição de tela) de aplicativos de terceiros.
* **H2:** Falha de vínculo ou autenticação entre launchers (Steam/Rockstar).
* **H3:** Arquivos de instalação do jogo corrompidos ou ausentes.
* **H4:** Superaquecimento (Thermal Throttling) causando limitação de hardware.
* **H5:** Drivers de vídeo desatualizados ou incompatíveis com o sistema atual.
* **H6:** Vazamento de memória (Memory Leak) ou falta de RAM disponível.
* **H7:** Falso positivo do sistema de segurança (Bloqueio por Antivírus).

---

## 3. Regras de Produção (Mínimo de 20)

As regras definem a lógica de inferência do sistema, utilizando a sintaxe `SE ... ENTÃO ...`.

### Regras de Conflito de Overlay (H1)
* **R01:** SE O jogo fecha sozinho para a área de trabalho E O overlay do Discord está ativado ENTÃO suspeita = Conflito de overlay.
* **R02:** SE O erro ocorre imediatamente ao tentar abrir o jogo E O overlay da Steam está ativado E O software Rivatuner ou MSI Afterburner está rodando em segundo plano ENTÃO hipótese = Conflito de overlay (sobreposição de tela) de aplicativos de terceiros.
* **R03:** SE Ocorre queda brusca de FPS durante o jogo E O overlay do GeForce Experience / AMD Adrenalin está ativado ENTÃO suspeita = Conflito de overlay.

### Regras de Launchers e Autenticação (H2)
* **R04:** SE O erro ocorre ao tentar iniciar pelo launcher da Steam E A conta da Rockstar Games foi vinculada à Steam E Ocorre falha de "Social Club failed to initialize" ENTÃO hipótese = Falha de vínculo ou autenticação entre launchers (Steam/Rockstar).
* **R05:** SE O erro ocorre ao tentar iniciar pelo launcher da Steam E Ocorre erro de autenticação de conta de terceiros ENTÃO hipótese = Falha de vínculo ou autenticação entre launchers (Steam/Rockstar).
* **R06:** SE A sincronização de arquivos na nuvem da Steam falhou E O jogo fecha sozinho para a área de trabalho ENTÃO hipótese = Falha de vínculo ou autenticação entre launchers (Steam/Rockstar).

### Regras de Arquivos Corrompidos / Mods (H3)
* **R07:** SE Uma mensagem de "Arquivo DLL ausente" ou "Corrompido" é exibida ENTÃO suspeita = Falha na integridade do jogo.
* **R08:** SE suspeita = Falha na integridade do jogo E O erro ocorre imediatamente ao tentar abrir o jogo ENTÃO hipótese = Arquivos de instalação do jogo corrompidos ou ausentes.
* **R09:** SE O jogo abre em segundo plano, mas não exibe imagem E Existem modificações não oficiais (Mods) instaladas no diretório do jogo ENTÃO hipótese = Arquivos de instalação do jogo corrompidos ou ausentes.
* **R10:** SE O áudio do jogo apresenta estalos, atrasos ou falhas E O jogo está instalado em um disco rígido mecânico (HDD) antigo ENTÃO suspeita = Falha na integridade do jogo.

### Regras de Superaquecimento (H4)
* **R11:** SE Ocorre queda brusca de FPS durante o jogo E A temperatura da CPU atinge mais de 85°C ENTÃO hipótese = Superaquecimento (Thermal Throttling) causando limitação de hardware.
* **R12:** SE A tela congela, mas o som do jogo continua rodando E A temperatura da GPU atinge mais de 85°C ENTÃO hipótese = Superaquecimento (Thermal Throttling) causando limitação de hardware.
* **R13:** SE O erro ocorre apenas após algumas horas de gameplay E A temperatura da CPU atinge mais de 85°C ENTÃO hipótese = Superaquecimento (Thermal Throttling) causando limitação de hardware.

### Regras de Drivers e Sistema (H5)
* **R14:** SE Ocorre queda brusca de FPS durante o jogo E O driver de vídeo (GPU) não é atualizado há mais de 6 meses ENTÃO hipótese = Drivers de vídeo desatualizados ou incompatíveis com o sistema atual.
* **R15:** SE Ocorreu uma tela azul (BSOD) durante a execução E O driver de vídeo (GPU) não é atualizado há mais de 6 meses ENTÃO hipótese = Drivers de vídeo desatualizados ou incompatíveis com o sistema atual.
* **R16:** SE O jogo apresenta artefatos visuais na tela E O Windows foi atualizado nos últimos 3 dias ENTÃO hipótese = Drivers de vídeo desatualizados ou incompatíveis com o sistema atual.

### Regras de Memória RAM (H6)
* **R17:** SE O uso da memória RAM chega a mais de 95% durante a execução E O erro ocorre apenas após algumas horas de gameplay ENTÃO hipótese = Vazamento de memória (Memory Leak) ou falta de RAM disponível.
* **R18:** SE O uso do disco (HD/SSD) fica em 100% constante E Os tempos de carregamento estão excessivamente longos ENTÃO hipótese = Vazamento de memória (Memory Leak) ou falta de RAM disponível.

### Regras de Antivírus e Permissões (H7)
* **R19:** SE O jogo fecha sozinho para a área de trabalho E Há uma notificação de falha de "Permissão de Administrador" ENTÃO hipótese = Falso positivo do sistema de segurança (Bloqueio por Antivírus).
* **R20:** SE O antivírus ou Windows Defender bloqueou o executável do jogo E Uma mensagem de "Arquivo DLL ausente" ou "Corrompido" é exibida ENTÃO hipótese = Falso positivo do sistema de segurança (Bloqueio por Antivírus).

---

## 4. Sugestão de Persistência (JSON)

Para facilitar a integração com o Módulo 3 (Motor de Inferência da P1), a base pode ser convertida para um formato estruturado como o exemplo abaixo:

```json
[
  {
    "id": "R04",
    "condicoes": [
      "O erro ocorre ao tentar iniciar pelo launcher da Steam",
      "A conta da Rockstar Games foi vinculada à Steam",
      "Ocorre falha de Social Club failed to initialize"
    ],
    "conclusao": "Falha de vínculo ou autenticação entre launchers (Steam/Rockstar)",
    "tipo": "hipotese"
  },
  {
    "id": "R01",
    "condicoes": [
      "O jogo fecha sozinho para a área de trabalho",
      "O overlay do Discord está ativado"
    ],
    "conclusao": "Conflito de overlay",
    "tipo": "suspeita"
  }
]