#include <pthread.h>
#include <iostream>

using std::cout;



void* messenger(void *ptr){
  char *message;
  message = (char *)ptr;
  cout << message;
  return (void*)0;
} // game_play()


int main(void){

  cout << "Hello World\n";

  pthread_t thread1, thread2;
  int  iret1, iret2;

  iret1 = pthread_create(&thread1, NULL, messenger, (void*) "Thread 1\n");
  iret2 = pthread_create(&thread2, NULL, messenger, (void*) "Thread 2\n");

  pthread_join( thread1, NULL);
  pthread_join( thread2, NULL); 

  printf("Thread 1 returns: %d\n",iret1);
  printf("Thread 2 returns: %d\n",iret2);

  return 0;
} // main()
