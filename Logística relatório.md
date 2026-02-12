# **1\. Resumo Executivo**

O presente relatório detalha a otimização da política de gestão de estoques de um Centro de Distribuição (CD) farmacêutico, transitando de uma abordagem estática (determinística) para uma modelagem estocástica dinâmica fundamentada na **Engenharia de Sistemas Logísticos**.

### **Contexto e Desafio**

A operação enfrentava um dilema clássico: como garantir a disponibilidade de medicamentos críticos sem inflar os custos de armazenagem. A análise inicial revelou que a utilização do Lote Econômico de Compra (EOQ) sem a devida proteção contra incertezas resultava em um desempenho operacional inaceitável em ambientes reais.

### **Metodologia e Descobertas**

Através de uma **Simulação de Eventos Discretos** (Seed 111), comparamos o modelo tradicional com uma política de Ponto de Ressuprimento (ROP) otimizada por **Estoque de Segurança (SS)**. Os principais achados foram:

* **Falha do Modelo Determinístico:** Ao ignorar a variabilidade da demanda e os atrasos do fornecedor, o sistema apresentou um custo de falta de **R$ 45.060,00**, com rupturas frequentes de estoque.  
* **Eficiência Estocástica:** A implementação de um Estoque de Segurança de **257 unidades** (para um Nível de Serviço Alvo de 95%) reduziu o custo total logístico em **74%**, caindo de R$ 52.326,30 para **R$ 13.463,82**.  
* **Desempenho Real:** O modelo proposto alcançou um Nível de Serviço de **91,7%**, estabilizando a operação mesmo diante de picos de demanda e instabilidades no *Lead Time*.

### **Decisão Recomendada**

Com base na análise de *trade-offs* e na fronteira eficiente de custos, recomenda-se:

1. **Adoção Imediata do Modelo Estocástico:** Fixar o Ponto de Ressuprimento (ROP) em **757 unidades** para absorver a variabilidade do sistema.  
2. **Monitoramento da Variabilidade:** Manter o monitoramento contínuo do desvio padrão do fornecedor, visto que a sensibilidade do sistema aponta que reduções na incerteza do *Lead Time* permitem liberações significativas de capital de giro retido em estoque de segurança.

# **2\. Contexto e Formulação do Problema (Síntese)**

**O objeto de estudo deste projeto é a operação logística da ElectroLog Distribuidora, focada no gerenciamento de estoques de componentes de alto giro e criticidade, representados pelo SKU-X100. Este item possui demanda volátil e é estratégico para o faturamento da empresa, exigindo níveis de disponibilidade superiores a 90%.**

### **2.1. O Problema Logístico**

**A gestão atual utiliza uma abordagem determinística baseada na média histórica de vendas e prazos de entrega. No entanto, a operação real enfrenta duas fontes de incerteza não capturadas pelo modelo atual:**

1. **Variabilidade da Demanda: Oscilações diárias que superam o consumo médio previsto.**  
2. **Incerteza do Suprimento: Atrasos aleatórios na entrega (*Lead Time*) por parte do fornecedor.**

**A incapacidade do modelo atual em absorver essas variações resulta em rupturas frequentes de estoque (*Stockouts*), gerando custos de oportunidade e multas contratuais, ao mesmo tempo em que períodos de baixa demanda geram custos excessivos de armazenagem.**

### **2.2. Justificativa do Tópico Central**

**A escolha do Tópico IV (Gestão de Estoques sob Incerteza) como eixo central deste trabalho justifica-se pela necessidade de abandonar premissas estáticas. A aplicação de modelos estocásticos permite calcular cientificamente o Estoque de Segurança (SS) necessário para atingir o Nível de Serviço Alvo, transformando a incerteza em uma variável de decisão financeira calculada, e não um risco operacional não gerenciado.**

### **2.3. Objetivos do Projeto**

**O objetivo principal é validar, através de simulação computacional, uma política de ressuprimento $(s, Q)$ que minimize o Custo Total Logístico.**

**As hipóteses de trabalho são:**

* **A demanda diária e o tempo de entrega são variáveis aleatórias independentes e normalmente distribuídas.**  
* **O custo de falta (*shortage cost*) é significativamente superior ao custo de manutenção, justificando o investimento em estoque de segurança.**

---

# ***3\. Dados e Preparação (C3)***

*A validade de uma simulação de eventos discretos depende diretamente da qualidade dos dados de entrada. Para este projeto, utilizou-se a geração de variáveis aleatórias sintéticas controladas por uma semente fixa (**Seed 111**), garantindo que os cenários de estresse sejam reprodutíveis e auditáveis.*

### ***3.1. Caracterização da Demanda (Figura 1\)***

*A demanda diária do SKU-X100 foi modelada como uma variável aleatória contínua seguindo uma Distribuição Normal ($N \\sim 100, 20$).*

*A análise do histograma gerado (**Figura 1**) revela uma dispersão simétrica. Embora a frequência modal esteja centralizada em 100 unidades, a simulação produziu dias de pico com consumo superior a 140 unidades.*

* ***Implicação:** Modelos baseados apenas na média ignoram essas caudas à direita (picos de consumo), que são justamente os dias causadores de ruptura de estoque.*

***\[INSERIR AQUI: Figura 1 (Histograma da Demanda \- Barra Azul)\]***

### ***3.2. Variabilidade do Suprimento (Figura 2\)***

*O tempo de ressuprimento (Lead Time) provou ser um fator crítico de incerteza. Modelado com média de 5 dias e desvio padrão de 1,5 dias, o histograma (**Figura 2**) demonstra que o fornecedor não é perfeitamente confiável.*

* ***Análise de Risco:** Sob a Seed 111, observaram-se ocorrências de entregas levando até **8 ou 9 dias**. Esses eventos de "cauda longa", embora menos frequentes, representam um desvio de quase 80% sobre o prazo médio, capaz de consumir inteiramente qualquer estoque de segurança mal dimensionado.*

***\[INSERIR AQUI: Figura 2 (Histograma do Lead Time \- Barra Laranja)\]***

### ***3.3. Parâmetros de Entrada da Simulação***

*Para garantir a transparência da modelagem financeira, consolidam-se abaixo os parâmetros econômicos e operacionais utilizados para alimentar o algoritmo em Python:*

***Tabela 1: Parâmetros de Entrada (Inputs)***

| *Parâmetro* | *Valor Adotado* | *Unidade* |
| :---- | :---- | :---- |
| ***Demanda Média ($\\mu\_d$)*** | *100* | *un/dia* |
| ***Desvio Padrão da Demanda ($\\sigma\_d$)*** | *20* | *un/dia* |
| ***Lead Time Médio ($\\mu\_L$)*** | *5* | *dias* |
| ***Desvio Padrão do Lead Time ($\\sigma\_L$)*** | *1.5* | *dias* |
| ***Custo de Pedido ($S$)*** | *R$ 150,00* | *por pedido* |
| ***Custo de Manutenção ($H$)*** | *R$ 5,00* | *un/ano* |
| ***Custo de Falta ($Shortage$)*** | *R$ 20,00* | *un/falta* |
| ***Nível de Serviço Alvo*** | *95%* | *($Z \\approx 1.645$)* |

# **4\. Implementação Computacional (C3)**

Para operacionalizar a análise proposta, desenvolveu-se um algoritmo de simulação em linguagem **Python**. O script foi estruturado para realizar uma **Simulação de Eventos Discretos (DES)** com incremento de tempo fixo (diário), permitindo a observação granular do comportamento do estoque ao longo de um horizonte de 365 dias.

### **4.1. Arquitetura e Bibliotecas**

O ambiente de desenvolvimento utilizou as seguintes bibliotecas científicas para garantir a precisão dos cálculos:

* **NumPy (numpy):** Utilizada para a geração de números pseudoaleatórios através da função numpy.random.RandomState, garantindo a estabilidade da semente (**Seed 111**) e a reprodutibilidade dos cenários estocásticos.  
* **SciPy (scipy.stats):** Empregada para o cálculo estatístico do Score Z (norm.ppf), fundamental para a definição precisa do fator de segurança dado o Nível de Serviço Alvo de 95%.  
* **Matplotlib e Seaborn:** Utilizadas para a plotagem gráfica dos histogramas e curvas de evolução do estoque.

### **4.2. Lógica do Motor de Simulação (simular\_estoque)**

O núcleo do código reside na função simular\_estoque, que modela a dinâmica operacional do armazém. Diferente de planilhas estáticas, esta função implementa a distinção técnica entre **Estoque Físico** (disponível para venda) e **Estoque de Posição** (Físico \+ Pedidos em Trânsito).

O algoritmo opera em um *loop* diário seguindo a seguinte lógica sequencial:

1. **Geração de Demanda:** A cada dia $t$, uma demanda $d\_t$ é gerada seguindo uma distribuição Normal ($N=100, \\sigma=20$), sendo arredondada para inteiros e limitada a valores não negativos.  
2. **Consumo e Ruptura:** A demanda é subtraída do estoque físico.  
   * Se $Estoque \< 0$, o sistema contabiliza o volume negativo como **Venda Perdida**, acumulando o custo de falta (total\_custo\_falta \+= abs(estoque) \* custo\_falta) e registrando a ruptura no ciclo.  
3. **Recebimento de Pedidos:** O sistema verifica se há um pedido pendente cuja data de chegada (dia\_chegada) coincide com o dia atual. Se sim, o lote $Q$ (EOQ) é adicionado ao estoque físico.  
4. **Revisão e Ressuprimento (Gatilho):** A decisão de compra segue a política de Revisão Contínua $(s, Q)$. O algoritmo verifica a condição:  
   $$EstoquePosicao \\leq ROP$$  
   Se verdadeira (e não houver pedido já pendente), um novo pedido é disparado. Neste momento, um *Lead Time* estocástico é gerado ($N=5, \\sigma=1.5$) para definir a data futura de chegada.

### **4.3. Definição dos Cenários no Código**

A robustez da implementação permite testar diferentes políticas apenas alterando os parâmetros de entrada da função, mantendo a mesma sequência aleatória de eventos (graças à Seed 111):

* **Cenário A:** Executado com ROP \= Demanda\_Media \* Lead\_Time\_Media (500 unidades).  
* **Cenário B:** Executado com ROP acrescido do Estoque de Segurança calculado pela fórmula do desvio padrão combinado, resultando em 757 unidades.

### **4.4. Saída de Dados e Métricas**

Ao final da execução, o algoritmo retorna um dicionário de dados contendo vetores diários (niveis, demandas) e escalares financeiros acumulados. O **Nível de Serviço** é calculado *ex-post* pela razão entre o número de ciclos sem ruptura e o total de ciclos de ressuprimento realizados, oferecendo uma métrica de desempenho real e não apenas teórica.

# **5\. Resultados, Cenários e Comparações**

A execução da simulação computacional permitiu observar o comportamento dinâmico do sistema de estoques sob a influência das variáveis aleatórias modeladas (Seed 111). Nesta seção, comparam-se os indicadores de desempenho operacional e financeiro entre a política atual (Cenário A) e a proposta (Cenário B).

### **5.1. Consolidação dos Resultados**

A Tabela 2 apresenta o resumo dos indicadores acumulados ao final do horizonte de simulação de 365 dias.

**Tabela 2: Resultados Comparativos da Simulação (Seed 111\)**

| Indicador | Cenário A (Determinístico) | Cenário B (Estocástico 95%) | Variação (%) |
| :---- | :---- | :---- | :---- |
| **Ponto de Ressuprimento (ROP)** | 500 un. | **757 un.** | \+51,4% |
| **Estoque de Segurança (SS)** | 0 un. | 257 un. | \- |
| **Custo de Pedido** | R$ 3.600,00 | R$ 3.600,00 | 0% |
| **Custo de Manutenção** | R$ 3.666,30 | R$ 4.923,82 | \+34,3% |
| **Custo de Falta (Penalidade)** | **R$ 45.060,00** | **R$ 4.940,00** | **\-89,0%** |
| **CUSTO TOTAL LOGÍSTICO** | **R$ 52.326,30** | **R$ 13.463,82** | **\-74,3%** |
| **Nível de Serviço Real** | 70,8% | 91,7% | \+29,5 p.p. |

### **5.2. Análise do Cenário A: O Colapso Determinístico**

A política baseada apenas nas médias ($\\mu\_d=100, \\mu\_L=5$) mostrou-se incapaz de absorver a variabilidade do sistema.

A **Figura 3** ilustra a evolução do estoque físico dia a dia. As áreas destacadas em vermelho representam períodos de ruptura (*stockouts*). Observa-se que, sempre que o *Lead Time* do fornecedor ultrapassou a média de 5 dias ou a demanda sofreu picos pontuais, o estoque de ciclo esgotou-se antes da chegada do ressuprimento.

* **Consequência:** O sistema operou com um Nível de Serviço de apenas **70,8%**, gerando um custo de falta astronômico de R$ 45.060,00, que representa 86% do custo total deste cenário.

**\[INSERIR AQUI: Figura 3 (Nível de Estoque Diário \- Cenário A)\]**

*Legenda: Evolução do estoque no Cenário Determinístico, evidenciando múltiplas rupturas (áreas vermelhas) devido à ausência de proteção contra variabilidade.*

### **5.3. Análise do Cenário B: A Eficácia da Proteção**

No Cenário B, o Ponto de Ressuprimento foi elevado para 757 unidades, incorporando um **Estoque de Segurança de 257 unidades**.

A **Figura 4** demonstra visualmente o efeito "amortecedor" dessa política. Embora o estoque tenha flutuado significativamente devido à incerteza da demanda (Seed 111), o nível mínimo raramente cruzou a linha de zero. O estoque de segurança absorveu os atrasos do fornecedor, mantendo a continuidade operacional.

* **Resultado:** O Nível de Serviço subiu para **91,7%**, próximo ao alvo teórico de 95%. A pequena discrepância deve-se à natureza finita da simulação (365 dias), onde eventos extremos de cauda na distribuição normal podem impactar a média amostral.

**\[INSERIR AQUI: Figura 4 (Nível de Estoque Diário \- Cenário B)\]**

*Legenda: Evolução do estoque no Cenário Estocástico. O aumento do ROP protege a operação, mitigando quase totalmente as rupturas.*

### **5.4. Análise Econômica Comparativa**

A **Figura 5** resume o impacto financeiro da decisão. Embora o Cenário B apresente um Custo de Manutenção 34% maior (devido ao estoque médio mais elevado), essa despesa adicional funciona como um "prêmio de seguro".

O investimento extra de aproximadamente R$ 1.250,00 em estocagem evitou uma perda de mais de R$ 40.000,00 em vendas e multas. O resultado global foi uma redução de **74,3% no Custo Total Logístico**, validando a hipótese de que, em ambientes incertos, o custo da falta supera largamente o custo da sobra.

**\[INSERIR AQUI: Figura 5 (Comparação de Custos: Cenário A vs B)\]**

*Legenda: Decomposição dos custos logísticos. Nota-se a eliminação quase total do Custo de Falta no Cenário B.*

# **6\. Tomada de Decisão e Análise de Trade-offs (C4)**

A decisão logística não se resume à minimização de custos isolados, mas à gestão inteligente de riscos e compensações (*trade-offs*). A simulação realizada permitiu construir a **Fronteira Eficiente** da operação, ferramenta essencial para alinhar a política de estoques com a estratégia financeira da empresa.

### **6.1. A Curva de Trade-off: Custo vs. Nível de Serviço**

A **Figura 6** apresenta a relação não linear entre o investimento necessário em estoques e a disponibilidade garantida ao cliente. A análise da curva revela o fenômeno dos **retornos decrescentes**:

1. **Zona de Eficiência (80% a 95%):** O custo total cresce de forma moderada para elevar o nível de serviço. O investimento marginal em estoque de segurança traz grandes ganhos em redução de rupturas.  
2. **Zona de Custo Exponencial (\> 96%):** Ao tentar atingir níveis de serviço próximos a 100%, a curva inclina-se verticalmente. Para eliminar o último 1% de risco de falta, seria necessário um aumento desproporcional no capital imobilizado.

**Decisão Estratégica:** A escolha do alvo de **95%** (adotado no Cenário B) situa-se no "joelho" da curva, representando o ponto ótimo onde o custo de manutenção e o custo de falta se equilibram de forma mais vantajosa para a ElectroLog.

**\[INSERIR AQUI: Figura 6 (Curva de Trade-off)\]**

*Legenda: Fronteira eficiente da operação. O ponto destacado em vermelho (95%) representa o equilíbrio ideal entre custo logístico total e nível de serviço.*

### **6.2. Análise de Sensibilidade: O Custo da Incerteza do Fornecedor**

Enquanto a demanda do cliente é uma variável externa (mercado), a incerteza do fornecedor é uma variável interna da cadeia de suprimentos que pode ser gerenciada. A **Figura 7** isola o impacto do Desvio Padrão do Lead Time ($\\sigma\_L$) sobre a necessidade de Estoque de Segurança (SS).

A simulação demonstra uma correlação direta e severa:

* Com um fornecedor estável ($\\sigma\_L \\approx 0$), o SS necessário seria mínimo (\< 50 unidades).  
* Com a instabilidade atual ($\\sigma\_L \= 1.5$), o SS sobe para 257 unidades.  
* Se a instabilidade piorar ($\\sigma\_L \> 3$), o SS necessário para manter 95% de serviço dobraria, tornando a operação financeiramente inviável.

**Insight Gerencial:** O gráfico prova que investir na homologação e desenvolvimento de fornecedores mais confiáveis (reduzindo $\\sigma\_L$) gera uma redução de custo de estoque mais efetiva do que apenas alterar o tamanho do lote de compra.

**\[INSERIR AQUI: Figura 7 (Sensibilidade à Incerteza do Lead Time)\]**

*Legenda: Impacto da variabilidade do fornecedor no dimensionamento do armazém. A instabilidade do Lead Time exige aumentos exponenciais no Estoque de Segurança.*

### **6.3. Recomendação Final**

Com base na análise quantitativa dos cenários e sensibilidades, recomenda-se:

1. **Implantar a Política Estocástica:** Fixar o ROP em 757 unidades imediatas.  
2. **Monitorar o Lead Time:** Estabelecer SLAs (*Service Level Agreements*) com o fornecedor para reduzir o desvio padrão da entrega, visando reduzir o Estoque de Segurança no próximo ciclo de revisão.

# **7\. Considerações sobre Comunicação e Reprodutibilidade (C5)**

A validade de um estudo de Engenharia não reside apenas nos seus resultados, mas na capacidade de auditá-los e comunicá-los de forma clara para a tomada de decisão. Este projeto foi estruturado sob os princípios de transparência e reprodutibilidade científica.

### **7.1. Reprodutibilidade Técnica**

Para garantir que a análise seja auditável e independente do analista, o código desenvolvido adota práticas rigorosas de Ciência de Dados:

* **Controle de Aleatoriedade:** A utilização da semente fixa (`Seed 111`) na biblioteca `NumPy` assegura que a sequência de demandas e atrasos gerada seja idêntica em qualquer execução futura. Isso permite que a auditoria verifique exatamente os mesmos cenários de ruptura e recuperação de estoque apresentados neste relatório.  
* **Padronização:** O uso de bibliotecas padrão de mercado (`Pandas`, `Matplotlib`, `SciPy`) garante que o modelo possa ser executado em qualquer ambiente Python sem dependências proprietárias.  
* **Código Aberto:** O *script* completo da simulação encontra-se disponível no **Apêndice A**, permitindo a verificação da lógica de cálculo dos custos e do nível de serviço.

### **7.2. Comunicação para Tomada de Decisão**

A complexidade estocástica foi traduzida em visualizações gerenciais intuitivas para facilitar a comunicação com *stakeholders* não técnicos:

* **Gráficos de "Dente de Serra" (Figuras 3 e 4):** Foram utilizados para demonstrar visualmente o risco. A marcação em vermelho das áreas negativas comunica instantaneamente o conceito de ruptura de estoque, sem necessidade de interpretação estatística complexa.  
* **Curva de Trade-off (Figura 6):** Serve como ferramenta de negociação entre os departamentos Financeiro e Comercial, explicitando quanto custa cada ponto percentual de melhoria no serviço ao cliente.

---

# **8\. Conclusão**

O presente estudo validou, através de **Simulação de Eventos Discretos (DES)**, a superioridade da Política de Revisão Contínua $(s, Q)$ sob incerteza em detrimento da modelagem determinística clássica. A execução do algoritmo computacional (Seed 111\) demonstrou que a premissa de normalidade nos parâmetros de entrada ($\\mu\_d, \\mu\_L$) não garante a estabilidade operacional quando se ignora a convolução das variâncias da demanda e do *Lead Time*.

A análise comparativa evidenciou que o modelo determinístico (Cenário A) é estruturalmente incapaz de absorver a estocasticidade do sistema. A variabilidade do fornecedor ($\\sigma\_L \= 1.5$) provocou rupturas cíclicas que degradaram o Nível de Serviço para **70,8%**, resultando em um Custo de Falta (*Stockout Cost*) de R$ 45.060,00, o que inviabiliza a operação sob a ótica da rentabilidade.

Em contrapartida, a calibração do modelo estocástico (Cenário B) através da introdução de um **Estoque de Segurança de 257 unidades** provou ser a solução ótima para o *trade-off* entre capital imobilizado e disponibilidade. Os resultados obtidos confirmam a hipótese inicial:

1. **Eficiência Operacional:** O sistema atingiu um Nível de Serviço de **91,7%**, estabilizando o atendimento mesmo diante de *outliers* de demanda e atrasos de fornecimento.  
2. **Otimização Financeira:** Houve uma redução de **74,3% no Custo Total Logístico** (de R$ 52.326,30 para R$ 13.463,82), validando que o custo marginal de manutenção do estoque de segurança é significativamente inferior ao custo de oportunidade das vendas perdidas.

Conclui-se que a implementação da política estocástica proposta posiciona a operação na região ótima da **Curva de Fronteira Eficiente**, mitigando riscos sistêmicos e garantindo a resiliência da cadeia de suprimentos sem incorrer em superdimensionamento de estoques (*Overstock*).

