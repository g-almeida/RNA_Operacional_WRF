FROM ubuntu:latest

RUN mkdir /wrf
RUN apt-get update
RUN apt-get -y install python3
RUN apt-get -y install python3-pip
RUN pip -y install pandas
RUN pip -y install matplotlib
RUN pip -y install seaborn
RUN pip -y install scikit-learn
#ADD . /app/

#ENTRYPOINT /bin/bash
#CMD ["dashbard-forecast.py"]