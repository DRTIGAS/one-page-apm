# Requisitos do Site APM Arquitetura

## Visão geral

- **Nome:** APM Arquitetura  
- **Objetivo principal:** gerar confiança e leads de pessoas que querem reformar, construir, otimizar espaços ou contratar consultoria.  
- **Tipo:** One-page responsiva com navegação por âncoras e URLs curtas.  
- **Público-alvo:**  
  - Pessoas físicas (apartamentos e casas).  
  - Pequenos negócios (salas comerciais, pequenos comércios).  
  - Clientes que precisam de consultoria pontual ou gestão de obras.

---

## 1. Tecnologia / Código / Integrações (Thiago Alves)

### 1.1 Estrutura e navegação

**Já implementado**
- One-page em HTML + Bootstrap 5 + CSS custom.  
- Seções principais: Home, Hero, Sobre a profissional, O que fazemos, Casos em destaque, Conteúdo educativo, Contato, Redes sociais, CTA final, Localização, Depoimentos, Tipos de projetos, Rodapé.  
- Navbar responsiva (desktop + mobile) com dropdown **Mais**.  
- Roteador simples com `history.pushState` para URLs curtas.

**Pendências**
- [ ] Testar todas as âncoras em desktop e mobile, ajustando `offset` se necessário.  
- [ ] Validar experiência se o JavaScript falhar (links de âncoras continuam funcionais, mas revisar rolagem).

### 1.2 Layout e responsividade

**Já implementado**
- Layout baseado em `container` / `row` / `col-*` do Bootstrap.  
- Carrossel na Home com componente `carousel` do Bootstrap.  
- Imagens responsivas (`.img-fluid`, `.ratio` para mapa).  
- Tipografia Inter via Google Fonts.

**Pendências**
- [ ] Ajustar tamanho/peso das imagens ao trocar para fotos reais.  
- [ ] Otimizar imagens (compressão) para a versão final.

### 1.3 Contato e formulários

**Já implementado**
- Formulário simples na seção **Contato** com campos:  
  - Nome  
  - E-mail ou WhatsApp  
  - Tipo de projeto (Reforma, Construção, Interiores, Consultoria)  
  - Mensagem livre  
- Envio atual via `mailto:` para o e-mail da arquiteta.

**Pendências / melhorias**
- [ ] Migrar o formulário para **Netlify Forms**:  
  - `method="POST" data-netlify="true"` e `<input type="hidden" name="form-name" value="contato-apm">`.  
  - Configurar o form `contato-apm` no painel Netlify com notificação por e-mail.
- [ ] Opcional: criar um segundo formulário para **Guia gratuito / Checklist** (captura apenas nome + e-mail).

### 1.4 Integrações externas

**Já implementado**
- WhatsApp com mensagem pré-preenchida para falar sobre reforma/construção.  
- Google Maps embed com localização **APM Arquitetura – Projetos e Interiores BH**.  
- Links de redes sociais (Instagram e TikTok) ainda genéricos.

**Pendências**
- [ ] Substituir URLs genéricas pelas contas reais:  
  - Instagram: `https://www.instagram.com/SEU_USUARIO`  
  - TikTok: `https://www.tiktok.com/@SEU_USUARIO`  
- [ ] Confirmar/atualizar o `src` do embed do Maps usando o link de **Incorporar um mapa** do Google Maps.

### 1.5 Deploy e infraestrutura

**Já implementado**
- Deploy estático no **Netlify**.  
- Arquivos de configuração:  
  - `_redirects` com `/* /index.html 200`.  
  - `netlify.toml` com redirect SPA para `/index.html`.  
- Domínio próprio configurado: `apmarquitetura.com.br`.

**Pendências**
- [ ] Garantir `publish = "."` como diretório de publicação (Netlify).  
- [ ] Revisar DNS (A/CNAME) e HTTPS (enforce HTTPS).  
- [ ] Consolidar fluxo de deploy via Git (commit → push → deploy automático).

---

## 2. Conteúdo / Produto / Marketing (Arquiteta + apoio)

### 2.1 Identidade profissional / Sobre

**Já presente**
- Nome: **Ana Paula Mendes de Sousa**.  
- Menção a **6 anos de carreira**.  
- Texto com foco em gestão de projetos e obras.

**Dados a completar**
- [ ] Faculdade e ano de formação.  
- [ ] Detalhes da especialização (instituição, curso, ano).  
- [ ] Registro profissional no CAU (ex.: `CAU: XX000000-0`).  
- [ ] CNPJ da empresa (rodapé).  
- [ ] Endereço ou bairro/região em BH.

### 2.2 Serviços (O que fazemos)

**Já configurado**
- Cards para:  
  - Projetos arquitetônicos completos.  
  - Consultoria técnica.  
  - Gestão de obras.  
  - Interiores e otimização de espaço.  
- Seção educativa **“Por que contar com um arquiteto na sua obra?”**.

**A ajustar**
- [ ] Detalhar exemplos reais em cada card (tipos de imóveis, situações comuns).  
- [ ] Opcional: indicar formatos de contratação (pacote, hora técnica etc.).

### 2.3 Portfólio e casos em destaque

**Já presente**
- Carrossel com imagens de exemplo (Unsplash).  
- Seção **“Casos reais em destaque”** com 2 cards genéricos.

**A completar**
- [ ] Substituir imagens por fotos de projetos reais (quando possível).  
- [ ] Ajustar títulos e descrições com dados reais por projeto: tipo de imóvel, metragem, bairro/cidade, objetivos, resultados.  
- [ ] Incluir ao menos 1 caso de consultoria/layout, se desejar.

### 2.4 Depoimentos e prova social

**Já presente**
- Seção **“O que os clientes dizem”** com 3 depoimentos de exemplo.  
- Faixa com badges de tipos de projetos/clientes.

**A completar**
- [ ] Substituir depoimentos por relatos reais (nome ou iniciais, tipo de projeto, bairro/cidade).  
- [ ] Incluir, se houver:  
  - Avaliações do Google (estrelinhas, média, trechos).  
  - Link para o perfil no Google Maps/Business.

### 2.5 Conteúdo educativo / Guia gratuito

**Já presente**
- Seção com benefícios de ter arquiteto.  
- Texto: “Em breve: guia gratuito com checklist para iniciar sua reforma”.

**A fazer**
- [ ] Criar o conteúdo do guia (PDF ou página): checklist prático para iniciar reforma.  
- [ ] Disponibilizar o arquivo no projeto (`guia-reforma-apm.pdf`).  
- [ ] Ajustar o bloco "Conteúdo extra" com botão real de download.  
- [ ] (Opcional) Capturar e-mail antes do download (Netlify Forms).

### 2.6 Redes sociais e presença digital

**Já presente**
- Bloco **“Acompanhe o dia a dia da APM Arquitetura”** com ícones de Instagram e TikTok.  
- Ícones também no rodapé.

**A completar**
- [ ] Informar `@` reais de cada rede.  
- [ ] Ajustar textos para refletir o conteúdo real postado (bastidores, antes/depois, dicas).  
- [ ] Decidir se adiciona outras redes (Pinterest, YouTube, LinkedIn).

---

## 3. Operacional / Atendimento (Arquiteta)

### 3.1 Processo de atendimento

**Já descrito**
- 1. Conversa inicial (briefing, orçamento, prazos).  
- 2. Projeto (estudos, layout, detalhamento).  
- 3. Obra (gestão, visitas, apoio técnico).  
- 4. Entrega (ajustes finais, orientações).

**A completar (interno, mas pode ir ao site)**
- [ ] Tempo médio de resposta a contatos (ex.: até 1 dia útil).  
- [ ] Canais oficiais de atendimento (WhatsApp, e-mail, redes).  
- [ ] Critérios de filtro de leads (região atendida, tipos de projeto prioritários).

---

## 4. Resumo feito x a fazer

### Já feito em código

- Estrutura completa da one-page em Bootstrap.  
- Navegação responsiva + URLs curtas.  
- Hero claro com serviços, região e CTAs.  
- Seções: Home, Sobre, O que fazemos, Casos em destaque, Conteúdo educativo, Contato, Redes sociais, CTA final, Localização, Depoimentos, Tipos de projetos, Rodapé.  
- Integrações: WhatsApp, Google Maps (embed), links de redes sociais.  
- Deploy no Netlify com domínio próprio e SPA configurado.

### A fazer (principais itens de conteúdo)

- [ ] Preencher dados reais: formação, especialização, CAU, CNPJ, endereço/bairro.  
- [ ] Trazer fotos reais de projetos e ajustar textos de portfólio.  
- [ ] Inserir depoimentos reais e avaliações do Google (se houver).  
- [ ] Substituir URLs genéricas de Instagram/TikTok pelos perfis reais.  
- [ ] Criar e disponibilizar o guia/checklist de reforma.  
- [ ] Migrar formulário de contato para Netlify Forms (opcional, recomendado).
