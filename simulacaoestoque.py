# -*- coding: utf-8 -*-
"""
======================================================
Compara dois cenários de gerenciamento de estoque:
  • Cenário A – ROP determinístico (sem estoque de segurança)
  • Cenário B – ROP estocástico (com estoque de segurança, nível de serviço 95%)

Seed  : 111
"""

import sys
import os

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import norm

# ══════════════════════════════════════════════════════════════════════════════
# 1. PARÂMETROS GLOBAIS
# ══════════════════════════════════════════════════════════════════════════════
SEED = 111
np.random.seed(SEED)

HORIZONTE = 365                    # dias
DEMANDA_MEDIA = 100                # μ_d (unidades/dia)
DEMANDA_DESVIO = 20                # σ_d

LEAD_TIME_MEDIO = 5                # μ_L (dias)
LEAD_TIME_DESVIO = 1.5             # σ_L

CUSTO_PEDIDO = 150.0               # S  (R$/pedido)
CUSTO_MANUTENCAO = 5.0             # H  (R$/un/ano)
CUSTO_FALTA = 20.0                 # Shortage (R$/un perdida)

NIVEL_SERVICO_ALVO = 0.95          # Para cenário B
Z_SCORE = norm.ppf(NIVEL_SERVICO_ALVO)   # ≈ 1.645

# ══════════════════════════════════════════════════════════════════════════════
# 2. CÁLCULOS ANALÍTICOS (EOQ, ROP, SS)
# ══════════════════════════════════════════════════════════════════════════════
demanda_anual = DEMANDA_MEDIA * HORIZONTE  # D anual

# EOQ clássico: Q* = sqrt(2·D·S / H)
EOQ = np.sqrt(2 * demanda_anual * CUSTO_PEDIDO / CUSTO_MANUTENCAO)
EOQ = round(EOQ)

# ── Cenário A: ROP determinístico (sem segurança) ──────────────────────────
ROP_A = DEMANDA_MEDIA * LEAD_TIME_MEDIO                       # = 500 un

# ── Cenário B: ROP com estoque de segurança ─────────────────────────────────
SS_B = Z_SCORE * np.sqrt(
    LEAD_TIME_MEDIO * DEMANDA_DESVIO**2
    + DEMANDA_MEDIA**2 * LEAD_TIME_DESVIO**2
)
SS_B = round(SS_B)
ROP_B = DEMANDA_MEDIA * LEAD_TIME_MEDIO + SS_B


# ══════════════════════════════════════════════════════════════════════════════
# 3. FUNÇÃO DE SIMULAÇÃO DIA-A-DIA
# ══════════════════════════════════════════════════════════════════════════════
def simular_estoque(Q: int, ROP: int, horizonte: int = HORIZONTE,
                    demanda_media: float = DEMANDA_MEDIA,
                    demanda_desvio: float = DEMANDA_DESVIO,
                    lt_media: float = LEAD_TIME_MEDIO,
                    lt_desvio: float = LEAD_TIME_DESVIO,
                    custo_pedido: float = CUSTO_PEDIDO,
                    custo_manutencao: float = CUSTO_MANUTENCAO,
                    custo_falta: float = CUSTO_FALTA,
                    seed: int | None = None) -> dict:
    """
    Simula o estoque dia a dia com política (Q, ROP).

    Retorna dicionário com:
        - niveis       : array de nível de estoque real por dia
        - demandas     : array de demandas geradas
        - lead_times   : lista de lead-times realizados
        - custo_pedido : custo total de pedidos
        - custo_manut  : custo total de manutenção
        - custo_falta  : custo total de falta
        - custo_total  : soma dos três custos
        - nivel_servico: fração de ciclos sem ruptura
    """
    if seed is not None:
        rng = np.random.RandomState(seed)
    else:
        rng = np.random.RandomState()

    # Estado inicial
    estoque = Q + ROP  # começar com estoque confortável
    estoque_posicao = estoque  # posição = real + em trânsito
    pedido_pendente = False
    dia_chegada = -1

    niveis = np.zeros(horizonte)
    demandas = np.zeros(horizonte)
    lead_times_list = []

    total_custo_pedido = 0.0
    total_custo_falta = 0.0
    unidades_em_estoque_dia = 0.0   # para custo de manutenção

    ciclos_total = 0
    ciclos_sem_ruptura = 0
    ruptura_no_ciclo = False

    for dia in range(horizonte):
        # 3a. Gerar demanda do dia
        d = rng.normal(demanda_media, demanda_desvio)
        d = max(0, round(d))
        demandas[dia] = d

        # 3b. Consumir estoque
        estoque -= d
        estoque_posicao -= d

        # 3c. Verificar chegada de pedido
        if pedido_pendente and dia >= dia_chegada:
            estoque += Q
            estoque_posicao += Q  # posição já tinha sido somada na emissão?
            # Nota: estoque_posicao foi incrementado no momento da emissão,
            # mas devemos corrigir: re-sincronizar
            pedido_pendente = False

            # Fechar ciclo
            ciclos_total += 1
            if not ruptura_no_ciclo:
                ciclos_sem_ruptura += 1
            ruptura_no_ciclo = False

        # 3d. Registrar ruptura
        if estoque < 0:
            total_custo_falta += abs(estoque) * custo_falta
            ruptura_no_ciclo = True

        # 3e. Manutenção (apenas estoque ≥ 0)
        if estoque > 0:
            unidades_em_estoque_dia += estoque

        # 3f. Emitir novo pedido se necessário
        # Usa estoque virtual (posição) = estoque real + pedido em trânsito
        estoque_virtual = estoque + (Q if pedido_pendente else 0)
        if estoque_virtual <= ROP and not pedido_pendente:
            pedido_pendente = True
            lt = rng.normal(lt_media, lt_desvio)
            lt = max(1, round(lt))
            lead_times_list.append(lt)
            dia_chegada = dia + lt
            total_custo_pedido += custo_pedido

        niveis[dia] = estoque

    # Fechar último ciclo se havia pedido pendente
    if ciclos_total == 0:
        ciclos_total = 1  # evitar divisão por zero

    # Custo de manutenção anual → proporcional
    total_custo_manut = (unidades_em_estoque_dia / horizonte) * custo_manutencao

    nivel_servico = ciclos_sem_ruptura / ciclos_total if ciclos_total > 0 else 1.0

    return {
        "niveis": niveis,
        "demandas": demandas,
        "lead_times": lead_times_list,
        "custo_pedido": total_custo_pedido,
        "custo_manut": total_custo_manut,
        "custo_falta": total_custo_falta,
        "custo_total": total_custo_pedido + total_custo_manut + total_custo_falta,
        "nivel_servico": nivel_servico,
    }


# ══════════════════════════════════════════════════════════════════════════════
# 4. EXECUTAR CENÁRIOS A e B
# ══════════════════════════════════════════════════════════════════════════════
print("=" * 65)
print("  ETAPA 2 - SIMULACAO DE ESTOQUE SOB INCERTEZA")
print("=" * 65)

resultado_A = simular_estoque(Q=EOQ, ROP=ROP_A, seed=SEED)
resultado_B = simular_estoque(Q=EOQ, ROP=ROP_B, seed=SEED)

# ══════════════════════════════════════════════════════════════════════════════
# 5. RESUMO NO CONSOLE
# ══════════════════════════════════════════════════════════════════════════════
print(f"\n{'-'*65}")
print(f"  PARAMETROS CALCULADOS")
print(f"{'-'*65}")
print(f"  EOQ (Q*)          = {EOQ} unidades")
print(f"  ROP Cenario A     = {ROP_A} unidades (sem seguranca)")
print(f"  ROP Cenario B     = {ROP_B} unidades (com SS)")
print(f"  Estoque Seg. (SS) = {SS_B} unidades")
print(f"  Z (95%)           = {Z_SCORE:.4f}")

for label, res in [("A (Deterministico)", resultado_A),
                   ("B (Estocastico 95%)", resultado_B)]:
    print(f"\n{'-'*65}")
    print(f"  CENARIO {label}")
    print(f"{'-'*65}")
    print(f"  Custo de Pedido    = R$ {res['custo_pedido']:>12,.2f}")
    print(f"  Custo de Manutencao= R$ {res['custo_manut']:>12,.2f}")
    print(f"  Custo de Falta     = R$ {res['custo_falta']:>12,.2f}")
    print(f"  Custo Total        = R$ {res['custo_total']:>12,.2f}")
    print(f"  Nivel de Servico   = {res['nivel_servico']*100:.1f}%")

print(f"\n{'='*65}\n")

# ══════════════════════════════════════════════════════════════════════════════
# 6. GRÁFICOS
# ══════════════════════════════════════════════════════════════════════════════
sns.set_theme(style="whitegrid", palette="muted", font_scale=1.05)

PASTA_GRAFICOS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "graficos")
os.makedirs(PASTA_GRAFICOS, exist_ok=True)

dias = np.arange(HORIZONTE)

# ── BLOCO 1: Entendendo a Incerteza ─────────────────────────────────────────

# Fig 1 — Histograma da demanda simulada
fig1, ax1 = plt.subplots(figsize=(10, 5))
sns.histplot(resultado_A["demandas"], bins=30, kde=True, color="steelblue",
             edgecolor="white", ax=ax1)
ax1.axvline(DEMANDA_MEDIA, color="crimson", ls="--", lw=2,
            label=f"μ = {DEMANDA_MEDIA}")
ax1.set_title("Fig 1 — Distribuição da Demanda Diária Simulada", fontsize=14,
              fontweight="bold")
ax1.set_xlabel("Demanda (unidades)")
ax1.set_ylabel("Frequência")
ax1.legend()
plt.tight_layout()
fig1.savefig(os.path.join(PASTA_GRAFICOS, "fig1_histograma_demanda.png"), dpi=300, bbox_inches="tight")


# Fig 2 — Histograma do lead time simulado
todos_lt = resultado_A["lead_times"] + resultado_B["lead_times"]
fig2, ax2 = plt.subplots(figsize=(10, 5))
sns.histplot(todos_lt, bins=range(0, max(todos_lt) + 2), kde=False,
             color="darkorange", edgecolor="white", ax=ax2)
ax2.axvline(LEAD_TIME_MEDIO, color="crimson", ls="--", lw=2,
            label=f"μ = {LEAD_TIME_MEDIO} dias")
ax2.set_title("Fig 2 — Distribuição do Lead Time Simulado", fontsize=14,
              fontweight="bold")
ax2.set_xlabel("Lead Time (dias)")
ax2.set_ylabel("Frequência")
ax2.legend()
plt.tight_layout()
fig2.savefig(os.path.join(PASTA_GRAFICOS, "fig2_histograma_lead_time.png"), dpi=300, bbox_inches="tight")

# ── BLOCO 2: Comparação de Desempenho (Evolução Temporal) ───────────────────

# Fig 3 — Nível de estoque Cenário A
fig3, ax3 = plt.subplots(figsize=(14, 5))
niveis_A = resultado_A["niveis"]
cor = np.where(niveis_A >= 0, "steelblue", "crimson")

ax3.bar(dias, niveis_A, color=["steelblue" if v >= 0 else "crimson" for v in niveis_A],
        width=1.0, edgecolor="none")
ax3.axhline(0, color="black", lw=0.8)
ax3.axhline(ROP_A, color="green", ls="--", lw=1.2, label=f"ROP = {ROP_A}")
ax3.fill_between(dias, niveis_A, 0, where=niveis_A < 0,
                 color="crimson", alpha=0.3, label="Ruptura (estoque < 0)")
ax3.set_title("Fig 3 — Nível de Estoque Diário — Cenário A (Determinístico)",
              fontsize=14, fontweight="bold")
ax3.set_xlabel("Dia")
ax3.set_ylabel("Estoque (unidades)")
ax3.legend(loc="upper right")
plt.tight_layout()
fig3.savefig(os.path.join(PASTA_GRAFICOS, "fig3_estoque_cenario_A.png"), dpi=300, bbox_inches="tight")

# Fig 4 — Nível de estoque Cenário B
fig4, ax4 = plt.subplots(figsize=(14, 5))
niveis_B = resultado_B["niveis"]

ax4.bar(dias, niveis_B, color=["steelblue" if v >= 0 else "crimson" for v in niveis_B],
        width=1.0, edgecolor="none")
ax4.axhline(0, color="black", lw=0.8)
ax4.axhline(ROP_B, color="green", ls="--", lw=1.2, label=f"ROP = {ROP_B}")
ax4.axhline(SS_B, color="orange", ls=":", lw=1.5,
            label=f"Estoque de Segurança = {SS_B}")
ax4.fill_between(dias, niveis_B, 0, where=niveis_B < 0,
                 color="crimson", alpha=0.3, label="Ruptura (estoque < 0)")
ax4.set_title("Fig 4 — Nível de Estoque Diário — Cenário B (Estocástico, 95%)",
              fontsize=14, fontweight="bold")
ax4.set_xlabel("Dia")
ax4.set_ylabel("Estoque (unidades)")
ax4.legend(loc="upper right")
plt.tight_layout()
fig4.savefig(os.path.join(PASTA_GRAFICOS, "fig4_estoque_cenario_B.png"), dpi=300, bbox_inches="tight")

# ── BLOCO 3: Análise Econômica e Sensibilidade ──────────────────────────────

# Fig 5 — Comparação de custos (barras agrupadas)
fig5, ax5 = plt.subplots(figsize=(10, 6))
categorias = ["Custo de Pedido", "Custo de Manutenção", "Custo de Falta", "Custo Total"]
valores_A = [resultado_A["custo_pedido"], resultado_A["custo_manut"],
             resultado_A["custo_falta"], resultado_A["custo_total"]]
valores_B = [resultado_B["custo_pedido"], resultado_B["custo_manut"],
             resultado_B["custo_falta"], resultado_B["custo_total"]]

x = np.arange(len(categorias))
largura = 0.35
barras_A = ax5.bar(x - largura/2, valores_A, largura, label="Cenário A",
                   color="salmon", edgecolor="white")
barras_B = ax5.bar(x + largura/2, valores_B, largura, label="Cenário B",
                   color="mediumseagreen", edgecolor="white")

ax5.set_title("Fig 5 — Comparação de Custos: Cenário A vs B", fontsize=14,
              fontweight="bold")
ax5.set_ylabel("Custo (R$)")
ax5.set_xticks(x)
ax5.set_xticklabels(categorias, rotation=15, ha="right")
ax5.legend()

# Adicionar valores sobre as barras
for barra in barras_A:
    h = barra.get_height()
    ax5.annotate(f"R${h:,.0f}", xy=(barra.get_x() + barra.get_width()/2, h),
                 xytext=(0, 5), textcoords="offset points",
                 ha="center", va="bottom", fontsize=8)
for barra in barras_B:
    h = barra.get_height()
    ax5.annotate(f"R${h:,.0f}", xy=(barra.get_x() + barra.get_width()/2, h),
                 xytext=(0, 5), textcoords="offset points",
                 ha="center", va="bottom", fontsize=8)
plt.tight_layout()
fig5.savefig(os.path.join(PASTA_GRAFICOS, "fig5_comparacao_custos.png"), dpi=300, bbox_inches="tight")

# Fig 6 — Curva de Trade-off (Fronteira Eficiente)
print("Gerando curva de trade-off (variando nivel de servico 80% a 99%)...")
niveis_alvo = np.arange(0.80, 0.995, 0.01)
custos_tradeoff = []
servicos_obtidos = []

for ns_alvo in niveis_alvo:
    z = norm.ppf(ns_alvo)
    ss = z * np.sqrt(
        LEAD_TIME_MEDIO * DEMANDA_DESVIO**2
        + DEMANDA_MEDIA**2 * LEAD_TIME_DESVIO**2
    )
    ss = max(0, round(ss))
    rop = DEMANDA_MEDIA * LEAD_TIME_MEDIO + ss
    res = simular_estoque(Q=EOQ, ROP=rop, seed=SEED)
    custos_tradeoff.append(res["custo_total"])
    servicos_obtidos.append(res["nivel_servico"] * 100)

fig6, ax6 = plt.subplots(figsize=(10, 6))
ax6.plot(servicos_obtidos, custos_tradeoff, "o-", color="darkorchid",
         markersize=6, linewidth=2)
ax6.set_title("Fig 6 — Curva de Trade-off: Nível de Serviço vs Custo Total",
              fontsize=14, fontweight="bold")
ax6.set_xlabel("Nível de Serviço Obtido (%)")
ax6.set_ylabel("Custo Total (R$)")
ax6.grid(True, alpha=0.3)

# Destacar o ponto 95%
idx_95 = np.argmin(np.abs(np.array(niveis_alvo) - 0.95))
ax6.annotate(f"  95% -> R${custos_tradeoff[idx_95]:,.0f}",
             xy=(servicos_obtidos[idx_95], custos_tradeoff[idx_95]),
             fontsize=10, color="crimson", fontweight="bold")
ax6.plot(servicos_obtidos[idx_95], custos_tradeoff[idx_95], "s",
         color="crimson", markersize=10, zorder=5)
plt.tight_layout()
fig6.savefig(os.path.join(PASTA_GRAFICOS, "fig6_tradeoff_servico_custo.png"), dpi=300, bbox_inches="tight")

# Fig 7 — Impacto da Incerteza do Fornecedor (σ_L vs SS)
print("Gerando analise de sensibilidade do lead time...")
sigma_L_range = np.arange(0, 4.1, 0.25)
ss_necessarios = []
custos_sigma = []

for sigma_L in sigma_L_range:
    ss = Z_SCORE * np.sqrt(
        LEAD_TIME_MEDIO * DEMANDA_DESVIO**2
        + DEMANDA_MEDIA**2 * sigma_L**2
    )
    ss_necessarios.append(round(ss))
    rop = DEMANDA_MEDIA * LEAD_TIME_MEDIO + round(ss)
    res = simular_estoque(Q=EOQ, ROP=rop, seed=SEED,
                          lt_desvio=sigma_L)
    custos_sigma.append(res["custo_total"])

fig7, ax7a = plt.subplots(figsize=(10, 6))
color_ss = "teal"
color_custo = "tomato"

ax7a.plot(sigma_L_range, ss_necessarios, "s-", color=color_ss,
          linewidth=2, markersize=6, label="Estoque de Segurança (SS)")
ax7a.set_xlabel("Desvio Padrão do Lead Time — σ_L (dias)")
ax7a.set_ylabel("Estoque de Segurança (unidades)", color=color_ss)
ax7a.tick_params(axis="y", labelcolor=color_ss)

ax7b = ax7a.twinx()
ax7b.plot(sigma_L_range, custos_sigma, "o--", color=color_custo,
          linewidth=2, markersize=5, label="Custo Total")
ax7b.set_ylabel("Custo Total (R$)", color=color_custo)
ax7b.tick_params(axis="y", labelcolor=color_custo)

ax7a.set_title("Fig 7 — Impacto da Incerteza do Fornecedor no Estoque de Segurança",
               fontsize=14, fontweight="bold")

# Combinar legendas
lines_1, labels_1 = ax7a.get_legend_handles_labels()
lines_2, labels_2 = ax7b.get_legend_handles_labels()
ax7a.legend(lines_1 + lines_2, labels_1 + labels_2, loc="upper left")
plt.tight_layout()
fig7.savefig(os.path.join(PASTA_GRAFICOS, "fig7_impacto_incerteza_fornecedor.png"), dpi=300, bbox_inches="tight")

# ── Exibir todos os gráficos ────────────────────────────────────────────────
print(f"Todos os graficos foram salvos em: {PASTA_GRAFICOS}")
print("Exibindo...")
plt.show()
