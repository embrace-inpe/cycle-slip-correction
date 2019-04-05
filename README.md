<img src="sw_logo.png" width="64">

# GNSS Cycle-Slip Correction

Aplicação [Python](https://www.python.org/) para análise e correção perda de ciclos (_cycle-slip_) presentes em 
dados GNSS (rinex). 

*Total Eletron Content* ou **TEC**, é um importante descritor quantitativo, consistindo no número 
total de elétrons integrados entre dois pontos, ao longo de um tubo de um metro quadrado (transecto), ou seja, a 
densidade numérica colunar de elétrons. Frequentemente chamada de unidade TEC, definida como TECU, com valor aproximado
.

[EMBRACE](http://www2.inpe.br/climaespacial/portal/pt/).

***

#### AMBIENTE DE DESENVOLVIMENTO:

Após clonar o repositório [git](https://github.com/embrace-inpe/cycle-slip-correction) para um diretório em sua máquina, 
siga as instruções à seguir para executar o programa.

1. [Ambiente virtual Python `.venv`](#1-Criar-ambiente-Python-isolado-com-a-lib-virtualenv)
2. [Instalação de dependências `pip`](#2-instalando-dependncias)
3. [Versões do `RINEX`](#3-execuo-do-programa)
4. [Configurando as constantes](#4-execuo-do-programa)
5. [Execução do programa `main.py`](#5-execuo-do-programa)
6. [Como contribuir com o projeto?]()

#### 1. Criar ambiente Python isolado com a lib virtualenv
Navegar até o diretório `cycle-slip-correction/` e criar o ambiente isolado através do comando:

```console
$ python -m venv .venv
```

Para ativar a venv basta executar o comando: 

```console
$ source .venv/bin/activate
```
Se tudo correr bem o prefixo da máquina virtual deve aparecer no seu  console da seguinte forma:
```console
(.venv) usuario@maquina:<seu-diretorio>$ seus comandos aqui
```
Para desativar a venv e retornar ao ambiente padrão, execute o comando: 

```console
$ deactivate
```
#### 2. Instalando dependências
Dentro da pasta do projeto `cycle-slip-correction/` e com a venv ativada, execute o comando:

```console
$ pip install -r requirements.txt
```

#### 3. Versões do `RINEX`
O atual código garante análise e correção de _cycle-slip_ em arquivos `RINEX` de `3.01` a `3.03`.

#### 4. Configurando constantes
As constantes são definidas em `settings.py` e podem ser alteradas de acordo com a necessidade da análise, 
por exemplo, tipo requerido `REQUIRED_VERSION` (em caso de implementações futuras para versões mais 
antidas), constelações a serem verificadas `CONSTELLATIONS`, por exemplo `G` e `R`, para GPS e GLONASS, 
 respectivamente.

#### 5. Execução do programa
Com a `.venv` ativa, a chamada do programa deve ser feita através do script `main.py`. O parâmetro `-rinex_folder` 
descreve o diretório contendo os arquivos `RINEX` que serão analisados e, possivelmente, corrigidos. Um segundo 
parâmetro, é também oferecido `-rinex_output`, que indica a pasta onde serão salvos as possíveis correções. 
Por fim, `-verbose` (`True` ou `False`) imprime o status do programa em tempo de execução, conforme o exemplo:
```console
$ python main.py -rinex_folder /home/user/embrace/tec/rinex/ -rinex_output /home/user/embrace/tec/rinex/correction/ -verbose True
```
Se tudo correr bem, a saída do programa deve imprimir gradualmente, mensagens similares ao exemplo abaixo:
```console
[2019.04.04 11:49:19] {cycle_slip.py  :410 } INFO : >> Found 4 file(s) 
[2019.04.04 11:49:19] {cycle_slip.py  :419 } INFO : >>>> Reading rinex: ango2210.14o 
[2019.04.04 11:52:35] {cycle_slip.py  :315 } INFO : >>>> Detecting peaks on the 4th order final differences in rTEC... 
[2019.04.04 11:52:35] {cycle_slip.py  :241 } INFO : >>>>>> No discontinuities detected (by final differences) for PRN G01 
[2019.04.04 11:52:35] {cycle_slip.py  :318 } INFO : >>>> Finding discontinuities and correcting cycle-slips (PRN G01)... 
[2019.04.04 11:52:35] {cycle_slip.py  :315 } INFO : >>>> Detecting peaks on the 4th order final differences in rTEC... 
[2019.04.04 11:52:35] {cycle_slip.py  :243 } INFO : >>>>>> Discontinuities detected in [   3   30 1123 1147 1149 1162 2104] (not NaN) for PRN G02 
[2019.04.04 11:52:35] {cycle_slip.py  :318 } INFO : >>>> Finding discontinuities and correcting cycle-slips (PRN G02)... 
[2019.04.04 11:52:35] {cycle_slip.py  :331 } INFO : >>>>>> Indexes match (278): correcting cycle-slips... 
[2019.04.04 11:52:35] {cycle_slip.py  :331 } INFO : >>>>>> Indexes match (305): correcting cycle-slips... 
[2019.01.21 16:28:18] {helper.py      :403 } INFO : >>>> Previous rinex version 3.03. Systems: ['G', 'R']
[...]
```

#### 5. Como contribuir com o projeto?
O projeto de correção de _cycle-slip_ foi realizado como parte de outro projeto realizado dentro do Programa 
Monitoramento Brasileiro Clima Espacial [(EMBRACE/INPE)](http://www2.inpe.br/climaespacial/portal/pt/), em São José dos Campos, São Paulo. A medida que se utiliza, 
ou que novos formatos de arquivos e constelações GNSS venha a surgir, é necessário que se incorpore novas 
versões do código. 

Portanto, para contribuir com o projeto, leia atentamente procedimentos de **cópia** e **_pull-requests** de projetos, 
por exemplo, neste [link](https://leportella.com/pt-br/2017/04/17/como-contribuir-com-open-source.html) ou 
[neste](https://www.digitalocean.com/community/tutorials/como-criar-um-pull-request-no-github-pt).