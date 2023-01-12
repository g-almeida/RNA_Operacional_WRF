#!/bin/bash


############### Configuracao manual pelo usuario ##########################
export RODADA=00               #Horario da rodada do GFS
export PREV=4                  #Quantidade de dias de previsao
export NPROC=6                 #Quantidade de nucleos para processamento
export CONJUNTO=1             #reservado para futuros testes para ensemble
export RAIZ=/home/lammoc/wrf_operacional/operacional
export GFS=$RAIZ/gfs/0p25
export MPIRUN=/usr/lib64/openmpi/bin/mpirun
export GRADS=/usr/bin/grads
#export EMAIL=/usr/local/bin/sendEmail

#%%%%%%%%%%%%%%%%% configura os dias de previsao %%%%%%%%%%%%%%%%%%%%%%%%%%
PREVISAO_DATA=`date --date "$PREV days" +"%Y-%m-%d"`
export DATA=$(date +%Y-%m-%d)-00Z
echo $PREVISAO_DATA
export RUN_HOURS=`expr $PREV \* 24`
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

#%%%%%%%%%%%%%%%%% configura os diretorios complementares %%%%%%%%%%%%%%%%%
export SCRIPTS=$RAIZ/scripts
export WRF=$RAIZ/modelo
export RELATORIOS=$RAIZ/relatorios
export ARWPOST=$RAIZ/ARWpost
#export VENTOASCII=$RAIZ/vento
export FIGURAS=$RAIZ/figuras
export FIGTEMPORARIO=$RAIZ/figuras/temporario
#export ARMAZ=/mnt/disco4Tb/backup_1km
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

#%%%%%%%%%%%%%%%%% configura as datas necessarias %%%%%%%%%%%%%%%%%%%%%%%%%
export ANO_HOJE=$(date +%Y)
export MES_HOJE=$(date +%m)
export DIA_HOJE=$(date +%d)
export ANO_FUTURO=`date --date "$PREV days" +"%Y"`
export MES_FUTURO=`date --date "$PREV days" +"%m"`
export DIA_FUTURO=`date --date "$PREV days" +"%d"`
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

$SCRIPTS/crontab.sh
export CC=gcc
export FC=gfortran
export F77=gfortran
export F90=gfortran
export MPI=/usr/lib64/openmpi
export MPI_INC=/usr/include/openmpi-x86_64
export MPIFC=mpif90
export MPIF77=mpif90
export MPIF90=mpif90
export MPICC=mpicc
export NETCDF=/home/lammoc/instalacoes
export JASPERLIB=/home/lammoc/instalacoes/lib
export JASPERINC=/home/lammoc/instalacoes/include

export DISPLAY=:0.0
export NCARG_ROOT=/usr/local/ncl-6.5.0

export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/home/lammoc/instalacoes/lib/
export PATH=$PATH:$HOME/.local/bin:$HOME/bin:/home/lammoc/instalacoes/bin:/usr/lib64/openmpi/bin:$NCARG_ROOT/bin




#%%%%%%%%%%%%%%%% Baixa arquivos do GFS de 0.25 %%%%%%%%%%%%%%%%%%%%%%%%%%%
$SCRIPTS/baixa_gfs_0p25.sh



#%%%%%%%%%%%%%%%%%% Prepara relatorio %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
echo "****************************************************************************
Rodada de $DIA_HOJE / $MES_HOJE / $ANO_HOJE - Previsao para $PREV dias ($RUN_HOURS horas), com $NPROC nucleos." > $RELATORIOS/$DATA.relatorio.geral.txt
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


#tirar daqui a alteracao do namelist.input.

#%%%%%%%%%%%%%%%%% altera as datas dos namelists %%%%%%%%%%%%%%%%%%%%%%%%%%
echo -n "Alterando namelist.wps" >> $RELATORIOS/$DATA.relatorio.geral.txt
cat $SCRIPTS/namelist.wps.base | sed "s/ANO_HOJE/$ANO_HOJE/g ; s/MES_HOJE/$MES_HOJE/g ; s/DIA_HOJE/$DIA_HOJE/g ; s/RODADA/$RODADA/g ; s/ANO_FUTURO/$ANO_FUTURO/g ; s/MES_FUTURO/$MES_FUTURO/g ; s/DIA_FUTURO/$DIA_FUTURO/g " > $WRF/namelist.wps
echo "... ok!"  >> $RELATORIOS/$DATA.relatorio.geral.txt

echo -n "Alterando namelist.input" >> $RELATORIOS/$DATA.relatorio.geral.txt
cat $SCRIPTS/namelist.input.base | sed "s/ANO_HOJE/$ANO_HOJE/g ; s/MES_HOJE/$MES_HOJE/g ; s/DIA_HOJE/$DIA_HOJE/g ; s/RODADA/$RODADA/g ; s/ANO_FUTURO/$ANO_FUTURO/g ; s/MES_FUTURO/$MES_FUTURO/g ; s/DIA_FUTURO/$DIA_FUTURO/g ; s/RUN_HOURS/$RUN_HOURS/g" > $WRF/namelist.input
echo "... ok!"  >> $RELATORIOS/$DATA.relatorio.geral.txt
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

#%%%%%%%%%%%%%%%%% Limpa diretorio %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
echo -n "Limpando diretorio do WRF"   >> $RELATORIOS/$DATA.relatorio.geral.txt
cd $WRF
rm $WRF/GRIBF*
rm $WRF/FILE*
rm $WRF/PFIL*
rm $WRF/met_em*
rm $WRF/wrfo*
rm $ARWPOST/*.dat
rm $ARWPOST/*.ctl
echo "... ok!"  >> $RELATORIOS/$DATA.relatorio.geral.txt
##%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
$WRF/geogrid.exe

##%%%%%%%%%%%%%%%%% UNGRIB %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
echo -n "Link_grib"  >> $RELATORIOS/$DATA.relatorio.geral.txt
$WRF/link_grib.csh $GFS/gfs.t"$RODADA"z.p*
echo "... ok!" >> $RELATORIOS/$DATA.relatorio.geral.txt


echo -n "Ungrib.exe : " >> $RELATORIOS/$DATA.relatorio.geral.txt
cd $WRF
UNGRIB_I=$(date +"%Y-%m-%d-%T")
echo -n "iniciou em $UNGRIB_I" >> $RELATORIOS/$DATA.relatorio.geral.txt
$WRF/ungrib.exe > $RELATORIOS/$DATA.relatorio.ungrib
UNGRIB_F=$(date +"%Y-%m-%d-%T")
echo -n " e finalizou em $UNGRIB_F" >> $RELATORIOS/$DATA.relatorio.geral.txt
sleep 2
TESTE_UNGRIB=`cat $WRF/ungrib.log | grep "Successful" | awk {'print $5,$6,$7,$8,$9'}`
  if [ "$TESTE_UNGRIB" == "Successful completion of program ungrib.exe" ]; then
     echo " ... com sucesso!" >> $RELATORIOS/$DATA.relatorio.geral.txt
  else
     echo " ... ATENCAO: nao foi executado" >> $RELATORIOS/$DATA.relatorio.geral.txt
  fi
##%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#
##%%%%%%%%%%%%%%%%% METGRID %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
echo -n "Metgrid.exe: " >> $RELATORIOS/$DATA.relatorio.geral.txt
cd $WRF
METGRID_I=$(date +"%Y-%m-%d-%T")
echo -n "iniciou em $METGRID_I" >> $RELATORIOS/$DATA.relatorio.geral.txt
cd $WRF
$WRF/metgrid.exe > $RELATORIOS/$DATA.relatorio.metgrid
METGRID_F=$(date +"%Y-%m-%d-%T")
echo -n " e finalizou em $METGRID_F" >> $RELATORIOS/$DATA.relatorio.geral.txt
sleep 2
TESTE_METGRID=`cat $WRF/metgrid.log | grep "Successful" | awk {'print $5,$6,$7,$8,$9'}`
  if [ "$TESTE_METGRID" == "Successful completion of program metgrid.exe" ]; then
     echo " ... com sucesso!" >> $RELATORIOS/$DATA.relatorio.geral.txt
  else
     echo " ... ATENCAO: nao foi executado" >> $RELATORIOS/$DATA.relatorio.geral.txt
  fi
##%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


#for conjunto in 'seq 1 $CONJUNTOS'; do

    #COlocar aqui a alteracao do namelist.input
    #criar um namelist.input para cada conjunto

#%%%%%%%%%%%%%%%%% REAL %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
REAL_I=$(date +"%Y-%m-%d-%T")
rm $RELATORIOS/$DATA.relatorio.real
echo -n "Real.exe   : " >> $RELATORIOS/$DATA.relatorio.geral.txt
cd $WRF
echo -n "iniciou em $REAL_I" >> $RELATORIOS/$DATA.relatorio.geral.txt
cd $WRF
$WRF/real.exe
REAL_F=$(date +"%Y-%m-%d-%T")
cp $WRF/rsl.out.0000 $RELATORIOS/$DATA.relatorio.real
echo -n " e finalizou em $REAL_F" >> $RELATORIOS/$DATA.relatorio.geral.txt
sleep 2
TESTE_REAL=`cat $RELATORIOS/$DATA.relatorio.real | grep "SUCCESS" | awk {'print $3,$4,$5,$6,$7'}`
  if [ "$TESTE_REAL" == "real_em: SUCCESS COMPLETE REAL_EM INIT" ]; then
     echo " ... com sucesso!" >> $RELATORIOS/$DATA.relatorio.geral.txt
  else
     echo " ... ATENCAO: nao foi executado" >> $RELATORIOS/$DATA.relatorio.geral.txt
  fi
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

#%%%%%%%%%%%%%%%%% WRF %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
ulimit -s unlimited
WRF_I=$(date +"%Y-%m-%d-%T")
rm $RELATORIOS/$DATA.relatorio.real
echo -n "WRF.exe    : " >> $RELATORIOS/$DATA.relatorio.geral.txt
cd $WRF
rm -rf $WRF/rsl.*
echo -n "iniciou em $WRF_I" >> $RELATORIOS/$DATA.relatorio.geral.txt
$MPIRUN -np $NPROC $WRF/wrf.exe
WRF_F=$(date +"%Y-%m-%d-%T")
cp $WRF/rsl.out.0000 $RELATORIOS/$DATA.relatorio.wrf
echo -n " e finalizou em $WRF_F" >> $RELATORIOS/$DATA.relatorio.geral.txt
sleep 2
TESTE_WRF=`cat $RELATORIOS/$DATA.relatorio.wrf | grep "SUCCESS" | awk {'print $3, $4, $5, $6'}`
  if [ "$TESTE_WRF" == "wrf: SUCCESS COMPLETE WRF" ]; then
     echo " ... com sucesso!" >> $RELATORIOS/$DATA.relatorio.geral.txt
  else
     echo " ... ATENCAO: nao foi executado" >> $RELATORIOS/$DATA.relatorio.geral.txt
  fi
##%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#
##%%%%%%%%%%%%%%%% Gera arquivos ctl e dat para o Grads %%%%%%%%%%%%%%%%%%%%
#



### Aqui tem que colocar no nome do arquivo o numero do conjunto


###### d04 ######
#echo -n "Alterando namelist.ARWpost d04"  >> $RELATORIOS/$DATA.relatorio.geral.txt
#cat $SCRIPTS/namelist.ARWpost_d04.base | sed "s/ANO_HOJE/$ANO_HOJE/g ; s/MES_HOJE/$MES_HOJE/g ; s/DIA_HOJE/$DIA_HOJE/g ; s/RODADA/$RODADA/g ; s/ANO_FUTURO/$ANO_FUTURO/g ; s/MES_FUTURO/$MES_FUTURO/g ; s/DIA_FUTURO/$DIA_FUTURO/g " > $ARWPOST/namelist.ARWpost
#echo "... ok!"  >> $RELATORIOS/$DATA.relatorio.geral.txt
#ulimit -s unlimited
#ARWPOST_I=$(date +"%Y-%m-%d-%T")
#echo -n "ARWpost.exe    : " >> $RELATORIOS/$DATA.relatorio.geral.txt
#cd $ARWPOST
#echo -n "iniciou em $ARWPOST_I" >> $RELATORIOS/$DATA.relatorio.geral.txt
#$ARWPOST/ARWpost.exe  > $RELATORIOS/$DATA.relatorio.arwpost
#ARWPOST_F=$(date +"%Y-%m-%d-%T")
#echo -n " e finalizou em $ARWPOST_F" >> $RELATORIOS/$DATA.relatorio.geral.txt
#sleep 2
#TESTE_ARWPOST=`cat $RELATORIOS/$DATA.relatorio.arwpost | grep "Successful" | awk {'print $2, $3, $4, $5'}`
#  if [ "$TESTE_ARWPOST" == "Successful completion of ARWpost" ]; then
 #    echo " ... com sucesso!" >> $RELATORIOS/$DATA.relatorio.geral.txt
#  else
#     echo " ... ATENCAO: nao foi executado" >> $RELATORIOS/$DATA.relatorio.geral.txt
#  fi
#
#
##### d03 ######
echo -n "Alterando namelist.ARWpost d03"  >> $RELATORIOS/$DATA.relatorio.geral.txt
cat $SCRIPTS/namelist.ARWpost_d03.base | sed "s/ANO_HOJE/$ANO_HOJE/g ; s/MES_HOJE/$MES_HOJE/g ; s/DIA_HOJE/$DIA_HOJE/g ; s/RODADA/$RODADA/g ; s/ANO_FUTURO/$ANO_FUTURO/g ; s/MES_FUTURO/$MES_FUTURO/g ; s/DIA_FUTURO/$DIA_FUTURO/g " > $ARWPOST/namelist.ARWpost
echo "... ok!"  >> $RELATORIOS/$DATA.relatorio.geral.txt
ulimit -s unlimited
ARWPOST_I=$(date +"%Y-%m-%d-%T")
echo -n "ARWpost.exe    : " >> $RELATORIOS/$DATA.relatorio.geral.txt
cd $ARWPOST
echo -n "iniciou em $ARWPOST_I" >> $RELATORIOS/$DATA.relatorio.geral.txt
$ARWPOST/ARWpost.exe  > $RELATORIOS/$DATA.relatorio.arwpost
ARWPOST_F=$(date +"%Y-%m-%d-%T")
echo -n " e finalizou em $ARWPOST_F" >> $RELATORIOS/$DATA.relatorio.geral.txt
sleep 2
TESTE_ARWPOST=`cat $RELATORIOS/$DATA.relatorio.arwpost | grep "Successful" | awk {'print $2, $3, $4, $5'}`
  if [ "$TESTE_ARWPOST" == "Successful completion of ARWpost" ]; then
     echo " ... com sucesso!" >> $RELATORIOS/$DATA.relatorio.geral.txt
  else
     echo " ... ATENCAO: nao foi executado" >> $RELATORIOS/$DATA.relatorio.geral.txt
  fi

#### d02 ######
echo -n "Alterando namelist.ARWpost d02"  >> $RELATORIOS/$DATA.relatorio.geral.txt
cat $SCRIPTS/namelist.ARWpost_d02.base | sed "s/ANO_HOJE/$ANO_HOJE/g ; s/MES_HOJE/$MES_HOJE/g ; s/DIA_HOJE/$DIA_HOJE/g ; s/RODADA/$RODADA/g ; s/ANO_FUTURO/$ANO_FUTURO/g ; s/MES_FUTURO/$MES_FUTURO/g ; s/DIA_FUTURO/$DIA_FUTURO/g " > $ARWPOST/namelist.ARWpost
echo "... ok!"  >> $RELATORIOS/$DATA.relatorio.geral.txt
ulimit -s unlimited
ARWPOST_I=$(date +"%Y-%m-%d-%T")
echo -n "ARWpost.exe    : " >> $RELATORIOS/$DATA.relatorio.geral.txt
cd $ARWPOST
echo -n "iniciou em $ARWPOST_I" >> $RELATORIOS/$DATA.relatorio.geral.txt
$ARWPOST/ARWpost.exe  > $RELATORIOS/$DATA.relatorio.arwpost
ARWPOST_F=$(date +"%Y-%m-%d-%T")
echo -n " e finalizou em $ARWPOST_F" >> $RELATORIOS/$DATA.relatorio.geral.txt
sleep 2
TESTE_ARWPOST=`cat $RELATORIOS/$DATA.relatorio.arwpost | grep "Successful" | awk {'print $2, $3, $4, $5'}`
  if [ "$TESTE_ARWPOST" == "Successful completion of ARWpost" ]; then
     echo " ... com sucesso!" >> $RELATORIOS/$DATA.relatorio.geral.txt
  else
     echo " ... ATENCAO: nao foi executado" >> $RELATORIOS/$DATA.relatorio.geral.txt
  fi

#### d01 ######
echo -n "Alterando namelist.ARWpost d01"  >> $RELATORIOS/$DATA.relatorio.geral.txt
cat $SCRIPTS/namelist.ARWpost_d01.base | sed "s/ANO_HOJE/$ANO_HOJE/g ; s/MES_HOJE/$MES_HOJE/g ; s/DIA_HOJE/$DIA_HOJE/g ; s/RODADA/$RODADA/g ; s/ANO_FUTURO/$ANO_FUTURO/g ; s/MES_FUTURO/$MES_FUTURO/g ; s/DIA_FUTURO/$DIA_FUTURO/g " > $ARWPOST/namelist.ARWpost
echo "... ok!"  >> $RELATORIOS/$DATA.relatorio.geral.txt
ulimit -s unlimited
ARWPOST_I=$(date +"%Y-%m-%d-%T")
echo -n "ARWpost.exe    : " >> $RELATORIOS/$DATA.relatorio.geral.txt
cd $ARWPOST
echo -n "iniciou em $ARWPOST_I" >> $RELATORIOS/$DATA.relatorio.geral.txt
$ARWPOST/ARWpost.exe  > $RELATORIOS/$DATA.relatorio.arwpost
ARWPOST_F=$(date +"%Y-%m-%d-%T")
echo -n " e finalizou em $ARWPOST_F" >> $RELATORIOS/$DATA.relatorio.geral.txt
sleep 2
TESTE_ARWPOST=`cat $RELATORIOS/$DATA.relatorio.arwpost | grep "Successful" | awk {'print $2, $3, $4, $5'}`
  if [ "$TESTE_ARWPOST" == "Successful completion of ARWpost" ]; then
     echo " ... com sucesso!" >> $RELATORIOS/$DATA.relatorio.geral.txt
  else
     echo " ... ATENCAO: nao foi executado" >> $RELATORIOS/$DATA.relatorio.geral.txt
  fi


#####ajuste de nome dos arquivos para o site
export DATA_HOJE=$(date --date "0 days" +"%Y%m%d")
export DATA_2=$(date --date "1 days" +"%Y%m%d")
export DATA_3=$(date --date "2 days" +"%Y%m%d")
export DATA_4=$(date --date "3 days" +"%Y%m%d")

#cd $SCRIPTS
#echo -n " Gerando figuras para d04" >> $RELATORIOS/$DATA.relatorio.geral.txt
#$SCRIPTS/figuras_d04.sh
#$GRADS -lbcx "figuras_d04.gs"
#echo "... ok!"  >> $RELATORIOS/$DATA.relatorio.geral.txt

cd $SCRIPTS
echo -n " Gerando figuras para d03" >> $RELATORIOS/$DATA.relatorio.geral.txt
$SCRIPTS/figuras_d03.sh
$GRADS -lbcx "figuras_d03.gs"
echo "... ok!"  >> $RELATORIOS/$DATA.relatorio.geral.txt

cd $SCRIPTS
echo -n " Gerando figuras para d02" >> $RELATORIOS/$DATA.relatorio.geral.txt
$SCRIPTS/figuras_d02.sh
$GRADS -lbcx "figuras_d02.gs"
echo "... ok!"  >> $RELATORIOS/$DATA.relatorio.geral.txt

cd $SCRIPTS
echo -n " Gerando figuras para d01" >> $RELATORIOS/$DATA.relatorio.geral.txt
$SCRIPTS/figuras_d01.sh
$GRADS -lbcx "figuras_d01.gs"
echo "... ok!"  >> $RELATORIOS/$DATA.relatorio.geral.txt

############## Criando Meteogramas para DCNit ############################

cd $SCRIPTS
echo -n " Gerando Meteogramas" >> $RELATORIOS/$DATA.relatorio.geral.txt
$SCRIPTS/meteograma1.sh
$GRADS -pbcx "meteograma1.gs"
$SCRIPTS/meteograma2.sh
$GRADS -pbcx "meteograma2.gs"
$SCRIPTS/meteograma3.sh
$GRADS -pbcx "meteograma3.gs"

echo "... ok!"  >> $RELATORIOS/$DATA.relatorio.geral.txt


################# Defesa Civil de Niteroi ##################
# Coloca o logo da Defesa Civil de Niteroi na figura

cd /home/lammoc/wrf_operacional/operacional/dc_niteroi
./put_logo_dcnit.sh

# Envia figuras para a DC Niteroi COM marca d'agua da Defesa Civil
cd $SCRIPTS
echo "Enviando arquivos para DCNit" >> $RELATORIOS/$DATA.relatorio.geral.txt
HORA=`date +%T`
echo "Hora de inicio $HORA" >> $RELATORIOS/$DATA.relatorio.geral.txt
$SCRIPTS/put_wrf_operacional_dcnit.sh
echo "... ok!"  >> $RELATORIOS/$DATA.relatorio.geral.txt
Hfinal=`date +%T`
echo "Hora de termino de envio $Hfinal" >> $RELATORIOS/$DATA.relatorio.geral.txt



################ Criando arquivos ascii de saida ###################
cd $SCRIPTS
echo -n " Gerando arquivos ascii" >> $RELATORIOS/$DATA.relatorio.geral.txt
$SCRIPTS/dados_ascii.sh
$GRADS -lbcx "dados_ascii.gs"
mv prec202* temp202* vent202* dados_ascii/$ANO_HOJE
echo "... ok!"  >> $RELATORIOS/$DATA.relatorio.geral.txt

################ Extraindo dados para Rede Neural (DCNIT) ###################
cd $SCRIPTS
echo -n " Extraindo dados RN" >> $RELATORIOS/$DATA.relatorio.geral.txt
$SCRIPTS/dadosRN_pluv.sh

echo "... ok!"  >> $RELATORIOS/$DATA.relatorio.geral.txt


################ Fazendo Backup das Figuras  ###################
cd $SCRIPTS
echo -n " Fazendo Backup das Figuras" >> $RELATORIOS/$DATA.relatorio.geral.txt
$SCRIPTS/backup_figuras.sh

echo "... ok!"  >> $RELATORIOS/$DATA.relatorio.geral.txt


############### Figuras para o site da Ambmet ############

cd $SCRIPTS
echo -n "Enviando figuras para o site" >> $RELATORIOS/$DATA.relatorio.geral.txt
$SCRIPTS/envia_ftp.sh
echo "... ok!"  >> $RELATORIOS/$DATA.relatorio.geral.txt


#### AMBMET  ####
AMBMET_SCRIPTS=/home/lammoc/wrf_operacional/operacional/ambmet/scripts
cd $AMBMET_SCRIPTS
$AMBMET_SCRIPTS/ambmet.sh

# Envia as figuras para o site da Ambmet SEM a marca d'agua

$SCRIPTS/put_wrf_operacional.sh



#echo -n "Alterando nomes das figuras" >> $RELATORIOS/$DATA.relatorio.geral.txt
#$SCRIPTS/alteranomefiguras.sh
#echo "... ok!"  >> $RELATORIOS/$DATA.relatorio.geral.txt
#


#####Roda o script para gerar o meteograma do vento em horario local
##echo -n "Gerando meteogramas..." >> $RELATORIOS/$DATA.relatorio.geral.txt
##cd $SCRIPTS
##$SCRIPTS/meteograma_vento.sh
##
###   for REGIAO in `seq 1 38`; do
###      /usr/bin/convert "$ARWPOST/meteograma_horalocal_raia"$REGIAO".png" -crop 500x150+35+10 "$FIGURAS/COB_atm_meteogramavento_04_"$REGIAO"_"$ANO_HOJE""$MES_HOJE""$DIA_HOJE".png"
###   done
##echo "... ok!"  >> $RELATORIOS/$DATA.relatorio.geral.txt
##
##
###Roda o script para gerar o meteograma de Temperatura em horario local
##echo -n "Gerando meteogramas temperatura..." >> $RELATORIOS/$DATA.relatorio.geral.txt
##cd $SCRIPTS
##$SCRIPTS/meteograma_temperatura.sh
###   for REGIAO in `seq 1 38`; do
###      /usr/bin/convert "$ARWPOST/meteogramaTEMP_horalocal_raia"$REGIAO".png" -crop 500x150+35+10 "$FIGURAS/COB_atm_meteogramatemperatura_04_"$REGIAO"_"$ANO_HOJE""$MES_HOJE""$DIA_HOJE".png"
###   done
##echo "... ok!"  >> $RELATORIOS/$DATA.relatorio.geral.txt
##
##echo -n "Enviando para o servidor..." >> $RELATORIOS/$DATA.relatorio.geral.txt
##echo "$DIA_HOJE" >> $RELATORIOS/$DATA.relatorio.ftp
##$SCRIPTS/envia_ftp.sh >> $RELATORIOS/$DATA.relatorio.ftp.txt
##echo "... ok!"  >> $RELATORIOS/$DATA.relatorio.geral.txt
##
###cd $SCRIPTS
##$SCRIPTS/meteograma2dia_vento.sh
##$SCRIPTS/meteograma3dia_vento.sh
##$SCRIPTS/meteograma2dia_temperatura.sh
##$SCRIPTS/meteograma3dia_temperatura.sh
##
###$SCRIPTS/envia_ftp_diasfuturos.sh >> $RELATORIOS/$DATA.relatorio.ftp.txt
##
##
###Registra o espaco disponivel em disco
##export ESPACO=$(df -h | grep "/home" | awk {'print $3'})
##echo "Espaco disponivel em disco: $ESPACO " >> $RELATORIOS/$DATA.relatorio.geral.txt
##
######### Envia email com o relatorio ##############
##$EMAIL -f projetobgwrf@gmail.com -t rafaelhor@gmail.com -t iandragaud@lamma.ufrj.br -u "NUMA3 - WRF 1 km COB $AGORA" < $RELATORIOS/$DATA.relatorio.geral.txt -s smtp.gmail.com:587 -xu projetobgwrf -xp projetoguanabara
###
###cp $WRF/wrfo*  $ARMAZ
###cp $ARWPOST/*.dat $ARMAZ
###cp $ARWPOST/*.ctl $ARMAZ
#rm $WRF/wrfrst*
#rm $WRF/wrfo*

##
##ONTEM=$(date --date "-1 days" +"%Y-%m-%d")
###rm $WRF/wrfout*$ONTEM*
###rm $ARWPOST/"$ONTEM"*dat
###rm $ARWPOST/"$ONTEM"*ctl
##
###mv $WRF/wrfo*  $ARMAZ
###mv $ARWPOST/*.dat $ARMAZ
###mv $ARWPOST/*.ctl $ARMAZ
##
##fim_job=$WRF/fim_job.txt
##
##printf '%s\n' 'Arquivo gerado ao final da execução do WRF.' 'Verificar data de modificação do arquivo, para certificar a execução do sistema.' >$fim_job
