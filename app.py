import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

st.set_page_config(page_title="Projeto EK Profit", layout="wide")

# ----- Carregamento de Dados -----
def load_data():
    try:
        data = pd.read_csv('data.csv')
    except FileNotFoundError:
        data = pd.DataFrame(columns=[
            'Data', 'Local', 'Tempo (min)', 'Profit', 'Upou', 'Observações'
        ])
    return data

def load_boss_drops():
    try:
        drops = pd.read_csv('boss_drops.csv')
    except FileNotFoundError:
        drops = pd.DataFrame(columns=['Data', 'Boss', 'Item', 'Valor (GP)', 'Observações'])
    return drops

def salvar_dados(data):
    data.to_csv('data.csv', index=False)

def salvar_drops(drops):
    drops.to_csv('boss_drops.csv', index=False)

# ----- Utilitário para formatar duração -----
def formatar_duracao(minutos):
    horas = minutos // 60
    mins = minutos % 60
    if horas > 0:
        return f"{horas}h {mins}min"
    else:
        return f"{mins}min"

# ----- Carregamento inicial -----
data = load_data()
if 'Upou' in data.columns:
    data['Upou'] = pd.to_numeric(data['Upou'], errors='coerce').fillna(0).astype(int)

boss_drops = load_boss_drops()

# ----- Controle de Investimento Inicial -----
investimento_real = 578.40  # R$
objetivo_final = 10000.00   # R$
level_inicial = 486
level_atual = level_inicial + data['Upou'].sum()

st.title("💰 Projeto EK dos Sonhos — Dashboard v2")
st.markdown(f"**Level Atual do Personagem:** {level_atual}")

# ----- Formulário de Nova Hunt -----
st.sidebar.header("Adicionar Nova Hunt")
with st.sidebar.form("form_hunt"):
    data_hunt = st.date_input("Data da Hunt", value=datetime.today())
    local = st.text_input("Local da Hunt")
    tempo = st.number_input("Tempo (min)", min_value=0, step=1)
    profit = st.number_input("Profit (GP)", min_value=0, step=1000)

    upou_check = st.checkbox("Upou na Hunt?", key="upou_check")

    niveis_upados_input = st.number_input(
        "Níveis upados (preencha se upou)", min_value=1, step=1, value=1, key="niveis_upados"
    )

    observacoes = st.text_area("Observações")
    submit = st.form_submit_button("Adicionar Hunt")

    if submit:
        if upou_check:
            niveis_upados = niveis_upados_input if niveis_upados_input > 1 else 1
        else:
            niveis_upados = 0

        nova_hunt = {
            'Data': data_hunt.strftime('%Y-%m-%d'),
            'Local': local,
            'Tempo (min)': tempo,
            'Profit': profit,
            'Upou': niveis_upados,
            'Observações': observacoes
        }

        data = pd.concat([data, pd.DataFrame([nova_hunt])], ignore_index=True)
        salvar_dados(data)
        data = load_data()
        data['Upou'] = pd.to_numeric(data['Upou'], errors='coerce').fillna(0).astype(int)
        st.success("✅ Hunt adicionada com sucesso!")

# ----- Formulário de Drop de Boss -----
st.sidebar.header("Adicionar Drop de Boss")
with st.sidebar.form("form_boss_drop"):
    data_drop = st.date_input("Data do Drop", value=datetime.today(), key="data_drop")
    boss = st.text_input("Nome do Boss")
    item = st.text_input("Item Dropado")
    valor_item = st.number_input("Valor do Item (GP)", min_value=0, step=1000)
    obs_drop = st.text_area("Observações do Drop")
    submit_drop = st.form_submit_button("Adicionar Drop")

    if submit_drop:
        novo_drop = {
            'Data': data_drop.strftime('%Y-%m-%d'),
            'Boss': boss,
            'Item': item,
            'Valor (GP)': valor_item,
            'Observações': obs_drop
        }
        boss_drops = pd.concat([boss_drops, pd.DataFrame([novo_drop])], ignore_index=True)
        salvar_drops(boss_drops)
        boss_drops = load_boss_drops()
        st.success("✅ Drop de boss adicionado com sucesso!")

# ----- Interface com Abas -----
aba1, aba2 = st.tabs(["📋 Histórico e Cadastro", "📊 Gráficos e Análises"])

with aba1:
    st.subheader("📜 Histórico de Hunts")

    # Conversão de datas
    data['Data'] = pd.to_datetime(data['Data'])
    hoje = datetime.today()
    dia_da_semana = hoje.weekday()  # segunda = 0, domingo = 6
    domingo = hoje - pd.Timedelta(days=(dia_da_semana + 1) % 7)
    sabado = domingo + pd.Timedelta(days=6)

    mostrar_tudo_tabela = st.checkbox("🔁 Mostrar todas as hunts", value=False)

    if not mostrar_tudo_tabela:
        data_filtrada = data[(data['Data'] >= domingo) & (data['Data'] <= sabado)]
        st.caption(f"Exibindo hunts de **{domingo.strftime('%d/%m')}** a **{sabado.strftime('%d/%m')}**")
    else:
        data_filtrada = data

    # Adiciona coluna de duração formatada
    data_filtrada['Duração'] = data_filtrada['Tempo (min)'].apply(lambda x: formatar_duracao(int(x)))

    colunas_exibidas = ['Data', 'Local', 'Duração', 'Profit', 'Upou', 'Observações']
    st.dataframe(data_filtrada[colunas_exibidas], use_container_width=True)

    st.markdown("---")
    st.header("🐉 Drops de Bosses")

    st.subheader("🔍 Filtro de Drops por Boss")
    bosses_unicos = boss_drops['Boss'].unique().tolist()
    boss_selecionado = st.selectbox("Selecione um Boss", ["Todos"] + bosses_unicos)

    if boss_selecionado != "Todos":
        drops_filtrados = boss_drops[boss_drops['Boss'] == boss_selecionado]
    else:
        drops_filtrados = boss_drops

    st.dataframe(drops_filtrados, use_container_width=True)

    # ----- Análise de um Dia Específico -----
    st.markdown("---")
    st.header("📆 Análise de um Dia Específico")

    data_disponiveis = sorted(data['Data'].dt.date.unique())

    if data_disponiveis:
        data_escolhida = st.date_input("Selecione um dia para análise", value=data_disponiveis[-1], min_value=min(data_disponiveis), max_value=max(data_disponiveis))
        dados_do_dia = data[data['Data'].dt.date == data_escolhida]

        if not dados_do_dia.empty:
            total_minutos = dados_do_dia['Tempo (min)'].sum()
            total_profit = dados_do_dia['Profit'].sum()
            horas = total_minutos // 60
            minutos = total_minutos % 60

            st.success(f"📊 No dia **{data_escolhida.strftime('%d/%m/%Y')}** você jogou por **{horas}h {minutos}min** e acumulou **{total_profit:,.0f} GP** de profit.")
        else:
            st.info("Nenhuma hunt registrada para esse dia.")
    else:
        st.info("Nenhuma hunt registrada ainda para análise diária.")

# ----- Gráficos e Análises -----
with aba2:
    if not data.empty:
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📊 Profit por Hunt")
            fig, ax = plt.subplots(figsize=(8, 5))
            sns.barplot(x='Data', y='Profit', hue='Local', data=data, ax=ax, palette='viridis')
            plt.xticks(rotation=45)
            st.pyplot(fig)

        with col2:
            st.subheader("📈 Profit Acumulado")
            data_ordenada = data.sort_values('Data')
            data_ordenada['Profit Acumulado'] = data_ordenada['Profit'].cumsum()

            fig2, ax2 = plt.subplots(figsize=(8, 5))
            sns.lineplot(x='Data', y='Profit Acumulado', data=data_ordenada, marker='o', ax=ax2)
            plt.xticks(rotation=45)
            st.pyplot(fig2)

        st.subheader("🧬 Evolução de Level")
        data_ordenada['Level'] = level_inicial + data_ordenada['Upou'].cumsum()
        fig3, ax3 = plt.subplots(figsize=(8, 5))
        sns.lineplot(x='Data', y='Level', data=data_ordenada, marker='o', ax=ax3, color='orange')
        ax3.set_ylabel("Level")
        plt.xticks(rotation=45)
        st.pyplot(fig3)
    else:
        st.info("Nenhuma hunt registrada ainda.")

    if not drops_filtrados.empty:
        st.subheader("📊 Valor dos Itens Dropados")
        fig4, ax4 = plt.subplots(figsize=(8, 5))
        sns.barplot(x='Item', y='Valor (GP)', data=drops_filtrados, ax=ax4, palette='magma')
        plt.xticks(rotation=45)
        st.pyplot(fig4)

        st.subheader("🏆 Top 5 Drops Mais Valiosos")
        top_drops = drops_filtrados.sort_values(by='Valor (GP)', ascending=False).head(5)
        st.table(top_drops[['Boss', 'Item', 'Valor (GP)']])
    else:
        st.info("Nenhum drop registrado para esse boss.")

# ----- Controle Financeiro Real -----
st.markdown("---")
st.header("💸 Controle de Investimento Real")

st.write(f"**Investimento Inicial:** R$ {investimento_real:,.2f}")
st.write(f"**Meta Final:** R$ {objetivo_final:,.2f}")

# Conversão baseada na média de 36.5k GP por TC e R$0,224 por TC
gp_por_tc = 36_500
valor_por_tc = 0.224

total_profit_gp = data['Profit'].sum() if not data.empty else 0
total_drops_gp = boss_drops['Valor (GP)'].sum() if not boss_drops.empty else 0
total_geral_gp = total_profit_gp + total_drops_gp

# Conversão de GP para reais
total_profit_real = (total_geral_gp / gp_por_tc) * valor_por_tc

st.write(f"**Profit Acumulado In-Game (Hunts):** {total_profit_gp:,.0f} GP")
st.write(f"**Valor de Drops de Bosses:** {total_drops_gp:,.0f} GP")
st.write(f"**Total Geral (Hunts + Bosses):** {total_geral_gp:,.0f} GP")
st.write(f"**Valor Aproximado em R$:** R$ {total_profit_real:,.2f}")

percentual = (total_profit_real / objetivo_final) * 100
st.progress(min(percentual / 100, 1.0))
st.write(f"**Progresso da Meta:** {percentual:.2f}%")
