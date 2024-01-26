code Main

  -- OS Class: Project 3
  --
  -- <PUT YOUR NAME HERE>
  --

-----------------------------  Main  ---------------------------------

  function main ()
      InitializeScheduler ()

      SleepingBarberTest ()
      --GamingParlorTest ()

      ThreadFinish ()
    endFunction

-----------------------------  The Sleeping Barber   ---------------------------------

  
  var barberThread: Thread
  var cThreads: array [50] of Thread = new array of Thread { 50 of new Thread }

  const
    WAITING_CHAIRS = 5
  var
    sCustomers: Semaphore = new Semaphore
    sBarbers: Semaphore = new Semaphore
    sMutex: Semaphore = new Semaphore

    haircut_customer_barber_synchronizer: Semaphore = new Semaphore
    waiting: int = 0

  function SleepingBarberTest ()
      var
        i: int

      sCustomers.Init (0)
      sBarbers.Init (0)
      sMutex.Init (1)
      haircut_customer_barber_synchronizer.Init (0)

      for i = 0 to 9 -- 6 customer creation.
        cThreads[i] = new Thread
        cThreads[i].Init ("Customer")       
        cThreads[i].Fork (customer, i)      
      endFor

      
      barberThread = new Thread
      barberThread.Init("Barber")
      barberThread.Fork(barber,1)


      for i = 10 to 19
        cThreads[i] = new Thread
        cThreads[i].Init ("Customer")      
        cThreads[i].Fork (customer, i)      
      endFor

     
      WasteTime(2000)

      
      for i = 20 to 29
        cThreads[i] = new Thread
        cThreads[i].Init ("Customer")       
        cThreads[i].Fork (customer, i)      
      endFor

     
      WasteTime(1000000)
      print("WasteTime Timeout.")
      nl()

      for i = 30 to 49
        cThreads[i] = new Thread
        cThreads[i].Init ("Customer")      
        cThreads[i].Fork (customer, i)      
      endFor

      -- you will see at the end barber checks for customer and 
      -- then went asleep.

    endFunction



  class Customer

      superclass Object
      fields
        number: int
        gotHaircut: bool
      methods
        Init (n: int)
        PrintStatus ()
        PrintIdentity ()
        get_haircut ()
    endClass

    behavior Customer
      method Init (n: int)
          self.number = n
          gotHaircut = false
          self.PrintIdentity()
          print (" has entered the lobby.")
          nl()
          self.PrintStatus ()
        endMethod

      -- Print whether has got haircut or not.
      method PrintStatus ()
          self.PrintIdentity ()
          print ("has Haircut status : ")
          printBool (gotHaircut)
          nl ()
        endMethod

      -- tell customer's id(as an unique identifier)
      method PrintIdentity ()
          print ("     (Customer ")
          printInt (self.number)
          print (") ")
        endMethod

      method get_haircut ()
          haircut_customer_barber_synchronizer.Up ()
          self.gotHaircut = true
          self.PrintIdentity ()
          print("gets a haircut.")
          nl ()
          self.PrintStatus ()
        endMethod
    endBehavior



  function barber ()
      while true                
        print ("Barber: checks for customer")
        nl ()
        sCustomers.Down ()      
        sMutex.Down ()          
        print ("Barber: Finds ")
        printInt (waiting)
        print (" customers waiting.")
        nl()
        waiting = waiting - 1   
        sBarbers.Up ()          
        sMutex.Up ()            
        cut_hair()              
      endWhile
    endFunction

  -- WasteTime is for simulating "Hair cutting".
  function cut_hair()
      print("Barber: Begins cutting hair.")
      nl()

      -- I used this as somehow a VC to synchronized cut_Hair & getHairCut.
      haircut_customer_barber_synchronizer.Down ()
      WasteTime(2000)  
      print("Barber: Done cutting hair")
      nl()
    endFunction


  -- simple no operation loop.
  function WasteTime(len: int)
      var
        i: int

      for i = 0 to len
        -- no-op. 
      endFor
    endFunction


/*

void customer(void){
  down(&mutex);
  if (waiting < CHAIRS) {
    waiting = waiting + 1;
    up(&customers);
    up(&mutex);
    down(&barbers);
    get_haircut();
  } else {
    up(&mutex);
  }
}

*/

  function customer (cNum: int)
      var
        current_customer: Customer = new Customer

      current_customer.Init(cNum)
      sMutex.Down ()     

      if waiting < WAITING_CHAIRS

        print("Customer with id:")
        printInt(cNum)
        print(" Got a chair from waiting room's chair.")
        nl()   

        waiting = waiting + 1
        sCustomers.Up ()           
        sMutex.Up ()
        sBarbers.Down ()            
        current_customer.get_haircut () 

      else
        sMutex.Up ()                
        current_customer.PrintIdentity ()
        print (" leaves. (Waiting room full)")
        nl ()
      endIf
    endFunction


-----------------------------  Gaming Parlor Problem  ---------------------------------

  const
    MAX_DICE = 8

  var
    desk: FrontDesk -- lazy initialization
    team: array [8] of Thread = new array of Thread {8 of new Thread }

  function GamingParlorTest ()

      -- initial desk.
      desk = new FrontDesk
      desk.Init ()

      -- initial all 8 Gamers.
      team[0].Init ("A (Backgammon)")
      team[0].Fork (playGame, 4)

      team[1].Init ("B (Backgammon)")
      team[1].Fork (playGame, 4)

      team[2].Init ("C (Risk)")
      team[2].Fork (playGame, 5)

      team[3].Init ("D (Risk)")
      team[3].Fork (playGame, 5)

      team[4].Init ("E (Monopoly)")
      team[4].Fork (playGame, 2)

      team[5].Init ("F (Monopoly)")
      team[5].Fork (playGame, 2)

      team[6].Init ("G (Pictionary)")
      team[6].Fork (playGame, 1)

      team[7].Init ("H (Pictionary)")
      team[7].Fork (playGame, 1)
    endFunction

  function playGame(needDice: int)
      var
        i: int

      -- Each player plays 5 times.
      for i = 1 to 5
    
        desk.Request (needDice)

        -- DOC says:
        -- To simulate playing the game, simply call the Yield method.
        currentThread.Yield ()

        desk.Return (needDice)

      endFor
    endFunction



  class FrontDesk
    superclass Object
    fields
      monitor: Mutex
      numberOfAvailableDices: int
      cond: Condition
    methods
      Init ()
      Request (numberOfDice: int)
      Return (numberOfDice: int)
      PrintStatus (str: String, count: int)
  endClass

  behavior FrontDesk

    method Init ()
        
        -- at first all dices are available.
        self.numberOfAvailableDices = MAX_DICE
        -- init monitor
        monitor = new Mutex
        monitor.Init()
        -- init CV
        cond = new Condition
        cond.Init ()
      endMethod

    method Request (numberOfDice: int)
        var
          looping: bool = true

        monitor.Lock ()
        self.PrintStatus ("requests", numberOfDice)
      
        while looping == true
          if self.numberOfAvailableDices >= numberOfDice
            self.numberOfAvailableDices = self.numberOfAvailableDices - numberOfDice
            looping = false
          else
            -- wait til some releasers notify you.
            -- Note: sometimes you will notified indirectly by dice consumers! not releasers.
            cond.Wait (& monitor)
          endIf
        endWhile

        self.PrintStatus ("uses", numberOfDice)

        -- indirect notifires :) (however it did work without indirect notifiers.)
        cond.Signal (& monitor)
        monitor.Unlock ()

      endMethod

    method Return (numberOfDice: int)

        monitor.Lock ()

        self.numberOfAvailableDices = self.numberOfAvailableDices + numberOfDice

        self.PrintStatus ("releases ", numberOfDice)
        
        -- direct notifires :)).
        cond.Signal (& monitor)
        monitor.Unlock ()
      endMethod


    -- print news & tell the desk's dices status.
    method PrintStatus (str: String, count: int)
        print (currentThread.name)
        print (" ")
        print (str)
        print (" ")
        printInt (count)
        print(" number of dices.")
        nl()
        print ("Number of available dices : ")
        printInt (self.numberOfAvailableDices)
        nl()
      endMethod

  endBehavior

endCode
