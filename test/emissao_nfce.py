from pynfe.processamento.comunicacao import ComunicacaoSefaz
from pynfe.entidades.cliente import Cliente
from pynfe.entidades.emitente import Emitente
from pynfe.entidades.notafiscal import NotaFiscal
from pynfe.entidades.fonte_dados import _fonte_dados
from pynfe.processamento.serializacao import SerializacaoXML, SerializacaoQrcode
from pynfe.processamento.assinatura import AssinaturaA1
from pynfe.utils.flags import CODIGO_BRASIL
from decimal import Decimal
import datetime

certificado = "/home/user/certificado.pfx"
senha = 'senha'
uf = 'pr'
homologacao = True

# emitente
emitente = Emitente(
    razao_social='NF-E EMITIDA EM AMBIENTE DE HOMOLOGACAO - SEM VALOR FISCAL',
    nome_fantasia='Nome Fantasia da Empresa',
    cnpj='99999999000199',           # cnpj apenas números
    codigo_de_regime_tributario='1', # 1 para simples nacional ou 3 para normal
    inscricao_estadual='9999999999', # numero de IE da empresa
    inscricao_municipal='12345',
    cnae_fiscal='9999999',           # cnae apenas números
    endereco_logradouro='Rua da Paz',
    endereco_numero='666',
    endereco_bairro='Sossego',
    endereco_municipio='Paranavaí',
    endereco_uf='PR',
    endereco_cep='87704000',
    endereco_pais=CODIGO_BRASIL
)

# cliente
cliente = Cliente(
    razao_social='NF-E EMITIDA EM AMBIENTE DE HOMOLOGACAO - SEM VALOR FISCAL',
    tipo_documento='CPF',           #CPF ou CNPJ
    email='email@email.com',
    numero_documento='12345678900', # numero do cpf ou cnpj
    indicador_ie=9,                 # 9=Não contribuinte
    endereco_logradouro='Rua dos Bobos',
    endereco_numero='Zero',
    endereco_complemento='Ao lado de lugar nenhum',
    endereco_bairro='Aquele Mesmo',
    endereco_municipio='Brasilia',
    endereco_uf='DF',
    endereco_cep='12345123',
    endereco_pais=CODIGO_BRASIL,
    endereco_telefone='11912341234',
)

# Nota Fiscal
nota_fiscal = NotaFiscal(
   emitente=emitente,
   cliente=cliente,
   uf=uf.upper(),
   natureza_operacao='VENDA', # venda, compra, transferência, devolução, etc
   forma_pagamento=0,         # 0=Pagamento à vista; 1=Pagamento a prazo; 2=Outros.
   tipo_pagamento=1,
   modelo=65,                 # 55=NF-e; 65=NFC-e
   serie='1',
   numero_nf='111',           # Número do Documento Fiscal.
   data_emissao=datetime.datetime.now(),
   data_saida_entrada=datetime.datetime.now(),
   tipo_documento=1,          # 0=entrada; 1=saida
   municipio='4118402',       # Código IBGE do Município
   tipo_impressao_danfe=4,    # 0=Sem geração de DANFE;1=DANFE normal, Retrato;2=DANFE normal Paisagem;3=DANFE Simplificado;4=DANFE NFC-e;
   forma_emissao='1',         # 1=Emissão normal (não em contingência);
   cliente_final=1,           # 0=Normal;1=Consumidor final;
   indicador_destino=1,
   indicador_presencial=1,
   finalidade_emissao='1',    # 1=NF-e normal;2=NF-e complementar;3=NF-e de ajuste;4=Devolução de mercadoria.
   processo_emissao='0',      #0=Emissão de NF-e com aplicativo do contribuinte;
   transporte_modalidade_frete=9, # 9=Sem Ocorrência de Transporte.
   informacoes_adicionais_interesse_fisco='Mensagem complementar',
   totais_tributos_aproximado=Decimal('21.06'),
)

# Produto
nota_fiscal.adicionar_produto_servico(
    codigo='000328',                           # id do produto
    descricao='NOTA FISCAL EMITIDA EM AMBIENTE DE HOMOLOGACAO - SEM VALOR FISCAL',
    ncm='99999999',
    cfop='5102',
    unidade_comercial='UN',
    ean='SEM GTIN',
    ean_tributavel='SEM GTIN',
    quantidade_comercial=Decimal('12'),        # 12 unidades
    valor_unitario_comercial=Decimal('9.75'),  # preço unitário
    valor_total_bruto=Decimal('117.00'),       # preço total
    unidade_tributavel='UN',
    quantidade_tributavel=Decimal('12'),
    valor_unitario_tributavel=Decimal('9.75'),
    ind_total=1,
    icms_modalidade='102',
    icms_origem=0,
    icms_csosn='400',
    pis_modalidade='07',
    cofins_modalidade='07',
    valor_tributos_aprox=Decimal('21.06')
    )

# responsável técnico
nota_fiscal.adicionar_responsavel_tecnico(
    cnpj='99999999000199',
    contato='TadaSoftware',
    email='tadasoftware@gmail.com',
    fone='11912341234'
  )

# serialização
serializador = SerializacaoXML(_fonte_dados, homologacao=homologacao)
nfce = serializador.exportar()

# assinatura
a1 = AssinaturaA1(certificado, senha)
xml = a1.assinar(nfce)

# token de homologacao
token = '000001'

# csc de homologação
csc = 'N4EOUTEDXCOVCGNTWLFD4OJLHBWCWJHCXC0C'

# gera e adiciona o qrcode no xml NT2015/003
xml_com_qrcode = SerializacaoQrcode().gerar_qrcode(token, csc, xml)

# envio
con = ComunicacaoSefaz(uf, certificado, senha, homologacao)
envio = con.autorizacao(modelo='nfce', nota_fiscal=xml_com_qrcode)

# em caso de sucesso o retorno será o xml autorizado
# Ps: no modo sincrono, o retorno será o xml completo (<nfeProc> = <NFe> + <protNFe>)
# no modo async é preciso montar o nfeProc, juntando o retorno com a NFe
from lxml import etree
if envio[0] == 0:
  print('Sucesso!')
  print(etree.tostring(envio[1], encoding="unicode").replace('\n','').replace('ns0:',''))
# em caso de erro o retorno será o xml de resposta da SEFAZ + NF-e enviada
else:
  print('Erro:')
  print(envio[1].text) # resposta
  print('Nota:')
  print(etree.tostring(envio[2], encoding="unicode")) # nfe