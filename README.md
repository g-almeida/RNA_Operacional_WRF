# RNA_Operacional_WRF
Aplicação de rede neural artificial multilayer perceptron para otimização do WRF operacional.

### . Alterações

Faça commits regulares e modificações em assuntos pontuais. Tenha certeza de estar trabalhando na sua branch e de que sabe quais arquivos serão commitados com ```git status```. Em caso de necessidade, remova algum arquivo do commit com ```git reset seu-arquivo```.

### . Guia de commits

Um commit deve ser curto e claro. Exemplo:

:bulb: novas docstrings para os métodos X e Y

Para ilustrar a ideia geral do seu commit, use o guia de emojis.

:tada: [tada] commit inicial, novo branch e afins  
:rocket: [rocket] quando adicionar arquivos ou funcionalidades  
:bug: [bug] quando corrigir bugs ou issues  
:poop: [poop] quando subir código ruim (a melhorar), porém funcional  
:scroll: [scroll] quando atualizar documentações  
:bulb: [bulb] quando atualizar documentação in-code  
:zap: [zap] quando aprimorar desempenho  
:package: [package] quando atualizar dependências, build e afins  
:wrench: [wrench] quando adicionar ou alterar arquivos de configuração  
:twisted_rightwards_arrows: [twisted_rightwards_arrows] quando unir branches  
:art: [art] quando aprimorar estilo, formatação ou corrigir alertas de lint do código  
:hammer: [hammer] quando refatorar  
:x: [x] quando remover códigos ou arquivos  
:construction: [construction] quando o trabalho estiver incompleto  
:pencil: [pencil] pequenas/ outras atualizações (melhoria de formatação, por exemplo)  
:ok_hand: [ok_hand] mudanças feitas durante code review  



### . Pre-process Pipeline

- Observed data
    main script: "API.py"
        responsible for bringing the hour observed data from the server.
    secondary script: "API_output_treatment.py"
        Brings together the once saved data from Barreto 1.xlsx and concats with the new values from the API.
        For this to work, we will need values for december-21, january-22, february-22. 

- WRF_output_treatment.py:
    inputs: 
        - extrai_rn.zip (WRF forecast compressed folder)
        - observed data (from )


