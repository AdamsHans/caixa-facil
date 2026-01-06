
### 🏦 Caixa Fácil - Sistema de Gestão de Caixa



Funcionalidades

📊 Gestão de Pagamentos

✅ Registro rápido de pagamentos com cliente, valor e forma

✅ Suporte para PIX, Crédito, Débito e Dinheiro

✅ Interface intuitiva com formulário único

✅ Visualização em cards coloridos por forma de pagamento

📁 Gestão de Comprovantes
✅ Upload de imagens (JPG, PNG)

✅ Organização automática em pasta comprovantes/

✅ Download em ZIP com arquivos estruturados

📈 Relatórios Inteligentes

✅ Totais automáticos por forma de pagamento

✅ Cálculo do total geral

✅ Exportação para CSV com codificação UTF-8

✅ Relatório ZIP contendo:

Arquivo CSV com todos os dados

Pasta com comprovantes organizados

🔒 Controle de Caixa

✅ Sistema de fechamento de caixa

✅ Bloqueio após fechamento

✅ Geração de relatório apenas após fechamento

✅ Interface de cores diferenciadas por tipo de pagamento

🛠️ Tecnologias

Python 3.10+ - Linguagem principal

Streamlit - Framework web

Pandas - Manipulação de dados

Zipfile - Compactação de arquivos

📦 Instalação

1. Clone o repositório
   
  git clone https://github.com/seu-usuario/caixa-facil.git
  cd caixa-facil
  
2. Crie um ambiente virtual (opcional mas recomendado)
   
   python -m venv venv
  # Linux/Mac:
  source venv/bin/activate
  # Windows:
  venv\Scripts\activate

3. Instale as dependências
   
  pip install -r requirements.txt

requirements.txt

  streamlit>=1.28.0
  pandas>=2.0.0

Como Executar

  streamlit run app.py

A aplicação estará disponível em: http://localhost:8501

🖥️ Interface

1. Registro de Pagamentos
   
  https://via.placeholder.com/600x300.png?text=Formul%C3%A1rio+de+Registro
  
  Data do caixa: Seleção do dia
  
  Cliente: Nome do cliente
  
  Valor: Valor em reais (formato decimal)
  
  Forma de pagamento: Dropdown com opções
  
  Comprovante: Upload opcional de imagem

2. Listagem Visual
   
  https://via.placeholder.com/600x300.png?text=Lista+de+Pagamentos
  
  Cards coloridos por forma de pagamento
  
  Botão de exclusão individual
  
  Indicador visual de comprovante

3. Totais
   
  https://via.placeholder.com/600x150.png?text=Tabela+de+Totais
  
  Resumo por forma de pagamento
  
  Total geral consolidado
  
  Layout em colunas responsivo

4. Fechamento e Relatório
   
  https://via.placeholder.com/600x200.png?text=Fechamento+de+Caixa
  
  Botão de fechamento de caixa
  
  Download de relatório ZIP
  
  CSV + comprovantes organizados

Cores por Forma de Pagamento

Forma	Cor	Ícone
PIX	Verde claro          🟢	    💳
Crédito	Azul claro       🔵	    💳
Débito	Laranja claro    🟠    	💳
Dinheiro	Amarelo claro  🟡	    💵

Estrutura do ZIP

  fechamento_caixa_2024-01-01.zip
├── relatorio_2024-01-01.csv
└── comprovantes/
    ├── 1_João_PIX.jpg
    ├── 2_Maria_Crédito.jpg
    └── 3_José_Débito.jpg

 Personalização
 
Modificar formas de pagamento:

  # No código, procure:
forma = st.selectbox(
    "Forma de pagamento",
    ["PIX", "Crédito", "Débito", "Dinheiro"]  # ← Adicione ou remova aqui
)

Alterar cores dos cards:

  # No código, procure:
def cor_card(forma):
    cores = {
        "PIX": "#d4f7dc",
        "Crédito": "#d0e0ff",
        # ← Adicione novas cores aqui
    }
    
🎯 Casos de Uso

Freelancers: Controle de recebimentos por projeto

Pequenos comércios: Fechamento diário de caixa

Profissionais liberais: Organização de pagamentos de clientes

Feirantes: Controle de vendas em eventos

Autônomos: Gestão simplificada de caixa

⚙️ Configuração Avançada

Persistência de Dados

O app atual usa session_state (dados em memória). Para persistência:

  Salvar em CSV local:

  import csv
# Adicionar no final do registro
with open('pagamentos.csv', 'a') as f:
    writer = csv.writer(f)
    writer.writerow([cliente, valor, forma, data_caixa])

Usar banco de dados SQLite:
     import sqlite3
  conn = sqlite3.connect('caixa.db')

# Criar tabela e operações CRUD

  Deploy na Nuvem
  
Streamlit Cloud (Recomendado)
Hugging Face Spaces
Render/Heroku com Docker

Contribuindo

Fork o projeto

Crie uma branch (git checkout -b feature/nova-funcionalidade)

Commit suas mudanças (git commit -m 'Add nova funcionalidade')

Push para a branch (git push origin feature/nova-funcionalidade)

Abra um Pull Request

📄 Licença
Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.

👨‍💻 Autor
Adams Hans

GitHub: https://github.com/AdamsHans

LinkedIn: https://www.linkedin.com/in/adamshans/

🙏 Agradecimentos
Equipe do Streamlit pela excelente ferramenta

Comunidade Python Brasil

Todos os contribuidores e testadores

⭐ Se este projeto ajudou você, dê uma estrela no GitHub!

