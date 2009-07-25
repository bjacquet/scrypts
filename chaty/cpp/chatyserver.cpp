
#include <QTcpServer>


class Server : public QTcpServer{
  Q_OBJECT

public:
  Server(QObject *parent = 0);
 };

Server::Server(QObject *parent) : QTcpServer(parent) {
     listen(QHostAddress::Any);
}


int main(void){
  
  Server servidor = new Server();

  return 0;
} // main()
