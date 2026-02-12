# Projeto de Simulação de Estoque Logístico

Este projeto implementa uma **Simulação de Eventos Discretos (DES)** para otimização da gestão de estoques, comparando cenários determinísticos e estocásticos.

## 📊 Dashboard Interativo

Acesse a simulação online:
🔗 **[https://projetologsticafelipesousamendes.streamlit.app/](https://projetologsticafelipesousamendes.streamlit.app/)**

---

## Estrutura do Projeto

- **`etapa2_simulacao_estoque.py`**: Script principal da simulação (gera gráficos e dados).
- **`dashboard_estoque.py`**: Aplicação web interativa (Streamlit).
- **`Relatorio_Final.tex`**: Código LaTeX do relatório técnico final.
- **`graficos/`**: Pasta com as figuras geradas pela simulação.

## Como executar localmente

1. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

2. Execute o dashboard:
   ```bash
   streamlit run dashboard_estoque.py
   ```
