# API
- /classes
  - [ ] /                   GET     list classes
  - [ ] /                   POST    create new class
    - title
  - [ ] /                   PUT     rename class
    - class_id
    - title
  - [ ] /                   DELETE  delete class, if no students, no exercises and no queries
  - [ ] /join               POST    join a class
    - class_id
  - [ ] /leave              POST    leave a class, if not teacher
    - class_id
  - [ ] /is-teacher         GET     is the user a teacher for this class?
    - class_id
  - [ ] /set-teacher        POST    set/unset participant as teacher
    - class_id
    - username
    - value
  - [ ] /members            GET     get participants in this class and their teacher status
    - class_id              
- /exercises        
  - [ ] /                   GET     list exercises in class
  - [ ] /                   POST    create new exercise in current class
  - [ ] /                   PUT     update exercise data
  - [ ] /                   DELETE  delete exercise, if there are no queries associated
    - exercise_id
  - [ ] /get                GET     get exercise data
    - exercise_id
  - [ ] /submit             POST    mark exercise as done
    - exercise_id
  - [ ] /unsubmit           POST    mark exercise as todo
    - exercise_id
  - [ ] /objectives         POST    set/unset learning objectives for this exercise
    - exercise_id
  - [ ] /objectives         GET     get objectives assigned to exercise
- /profile      
  - [ ] /                   GET     get profile data
- /auth     
  - [ ] /register           POST    register a new account
  - [ ] /login              POST    login with username/password
  - [ ] /reset-password     POST    set new password for username
- /datasets
  - [ ] /list               GET     list datasets avaiable to current user

# Pages
/

/profile
/profile/learning

/classes            GET     -> list classes
/classes/XFV45OT6   GET     -> list exercises

/exercises/56       GET     -> exercise data

/about

/login
/register

