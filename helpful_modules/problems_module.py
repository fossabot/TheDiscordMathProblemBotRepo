from typing import *
from time import sleep
from sqlite3 import *
from typing import *
import nextcord, json, warnings, dislash
from copy import deepcopy, copy
from nextcord import *
import pickle, sqlite3, traceback
from threading import Thread
import warnings
import sqldict #https://github.com/skylergrammer/sqldict/
import asyncio, aiosqlite
import sys
from .dict_factory import dict_factory #Attribution to stackoverflow

"""The core of my bot (very necessary)"""

main_cache = None
def get_main_cache():
    return main_cache
    


# This is a module containing MathProblem and MathProblemCache objects. (And exceptions as well!) This may be useful outside of this discord bot so feel free to use it :) Just follow the MIT+GNU license
#Exceptions
class MathProblemsModuleException(Exception):
    "The base exception for problems_module."
class TooLongArgument(MathProblemsModuleException):
    '''Raised when an argument passed into MathProblem() is too long.'''
    pass
class TooLongAnswer(TooLongArgument):
    """Raised when an answer is too long."""
    pass
class TooLongQuestion(TooLongArgument):
    """Raised when a question is too long."""
    pass
class GuildAlreadyExistsException(MathProblemsModuleException):
    "Raised when MathProblemCache.add_empty_guild tries to run on a guild that already has problems."
    pass
class ProblemNotFoundException(MathProblemsModuleException):
    "Raised when a problem is not found."
    pass
class TooManyProblems(MathProblemsModuleException):
    "Raised when trying to add problems when there is already the maximum number of problems."
    pass
class ProblemNotFound(KeyError):
    "Raised when a problem isn't found"
    pass
class ProblemNotWrittenException(MathProblemsModuleException):
    "Raised when trying to grade a written problem but the problem is not graded"
    pass

class QuizAlreadySubmitted(MathProblemsModuleException):
    "Raised when trying to submit a quiz that has already been submitted"
    pass

class SQLException(MathProblemsModuleException):
    "Raised when an error happens relating to SQL!"
class MathProblem:
    "For readability purposes :)"
    def __init__(self,question,answer,id,author,guild_id="_global", voters=[],solvers=[], cache=None,answers=[]):
        if guild_id != "_global" and not isinstance(guild_id, str):
            raise TypeError("guild_id is not an string")
        if not isinstance(id, int):
            raise TypeError("id is not an integer")
        if not isinstance(question, str):
            raise TypeError("question is not a string")
        if not isinstance(answer, str):
            raise TypeError("answer is not a string")
        if not isinstance(author, int):
            raise TypeError("author is not an integer")
        if not isinstance(voters, list):
            raise TypeError("voters is not a list")
        if not isinstance(solvers, list):
            raise TypeError("solvers is not a list")
        if not isinstance(answers, list):
            raise TypeError("answers isn't a list")
        
        if cache is None:
            warnings.warn("_cache is None. This may cause errors", RuntimeWarning)
        #if not isinstance(cache,MathProblemCache) and cache is not None:
        #    raise TypeError("_cache is not a MathProblemCache.")
        if len(question) > 250:
            raise TooLongQuestion(f"Your question is {len(question) - 250} characters too long. Questions may be up to 250 characters long.")
        self.question = question
        if len(answer) > 100:
            raise TooLongAnswer(f"Your answer is {len(question) - 100} characters too long. Answers may be up to 100 characters long.")
        self.answer = answer
        self.id = id
        self.guild_id = guild_id
        self.voters = voters
        self.solvers=solvers
        self.author=author
        self._cache = cache
        self.answers = answers
    def edit(self,question=None,answer=None,id=None,guild_id=None,voters=None,solvers=None,author=None, answers = None) -> None:
        """Edit a math problem. The edit is in place"""
        if guild_id not in [None,"_global"] and not isinstance(guild_id, int):
            raise TypeError("guild_id is not an integer")
        if not isinstance(id, int) and id is not None:
            raise TypeError("id is not an integer")
        if not isinstance(question, str) and question is not None:
            raise TypeError("question is not a string")
        if not isinstance(answer, str) and answer is not None:
            raise TypeError("answer is not a string")
        if not isinstance(author, int) and author is not None:
            raise TypeError("author is not an integer")
        if not isinstance(voters, list) and voters is not None:
            raise TypeError("voters is not a list")
        if not isinstance(solvers, list) and solvers is not None:
            raise TypeError("solvers is not a list")
        if not isinstance(answers, list) and answers is not None:
            raise TypeError("answers is not a list")
        if id is not None or guild_id is not None or voters is not None or solvers is not None or author is not None:
            warnings.warn("You are changing one of the attributes that you should not be changing.", category=RuntimeWarning)
        if question is not None:
            if (self._cache is not None and len(question) > self._cache.max_question_length) or (len(question) > 250 and self._cache is None):
                if self._cache is not None:
                    raise TooLongQuestion(f"Your question is {len(question) - self._cache.max_question_length} characters too long. Questions may be up to {self._cache.max_question_length} characters long.")
                else:
                    raise TooLongQuestion(f"Your question is {len(question) - 250} characters too long. Questions may be up to 250 characters long.")
            self.question = question
        if (self._cache is not None and len(question) > self._cache.max_question_length) or (len(answer) > 100 and self._cache is None):
            if self._cache is not None:
                raise TooLongAnswer(f"Your answer is {len(question) - self._cache.max_answer_length} characters too long. Answers may be up to {self._cache.max_answer_length} characters long.")
            else:
                raise TooLongAnswer(f"Your answer is {len(question) - 100} characters too long. Answers may be up to 100 characters long.")
        for answer in range(len(answers)):
            if self._cache is not None:
                if len(answers[answer]) > 100:
                    raise TooLongAnswer(f"Answer #{answer} is {len(answers[answer])-100} characters too long. Answers can be up to a 100 characters long")
            else:
                if len(answers[answer]) > self._cache.max_answer_length:
                    raise TooLongAnswer(f"Answer #{answer} is {len(answers[answer]) - self._cache.max_answer_length} characters too long. Answers can be up to {self._cache.max_answer_length} characters long.")
        if answer is not None:
            self.answer = answer
        if id is not None:
            self.id = id
        if guild_id is not None:
            self.guild_id = guild_id
        if voters is not None:
            self.voters = voters
        if solvers is not None:
            self.solvers = solvers
        if author is not None:
            self.author = author

        self.update_self()
    def update_self(self):
        "A helper method to update the cache with my version"
        if self._cache is not None:
            self._cache.update_problem(self.guild_id, self,id, self)

    @classmethod
    def from_row(cls, row, cache = None):
        try:
            answers = pickle.loads(row["answers"]) # Load answers from bytes to a list (which should contain only pickleable objects)!
            voters = pickle.loads(row["voters"]) #Do the same for voters and solvers
            solvers = pickle.loads(row["voters"])
            _Row = {
                "guild_id": row["guild_id"], # Could be None
                "problem_id": row["guild_id"],
                "answer": Exception, # Placeholder,
                "answers": answers,
                "voters": voters,
                "solvers": solvers,
                "author": row["author"]
            }
            return cls.from_dict(_Row, cache=cache) 
        except BaseException as e:
            traceback.print_exception(type(e), e, e.__traceback__, file = sys.stderr) # Log to stderr
            raise SQLException("Uh oh...") from e #Re-raise the exception to the user (so that they can help me debug (error_logs/** is gitignored))
    @classmethod
    def from_dict(cls,_dict, cache = None):
        "Convert a dictionary to a math problem. cache must be a valid MathProblemCache"
        assert isinstance(_dict, (dict, sqlite3.Row))
        problem = _dict
        guild_id = problem["guild_id"]
        if guild_id == "_global":
            guild_id = "_global"
        elif guild_id == "null": #Remove the guild_id null (used for global problems), which is not used anymore because of conflicts with SQL
        
            Problem = cls(
            question=problem["question"],
            answer=problem["answer"],
            id = int(problem["id"]),
            guild_id = "_global",
            voters = problem["voters"],
            solvers=problem["solvers"],
            author=problem["author"],
            cache = cache
        ) # Problem-ify the problem, but set the guild_id to _global
            #Then remove the problem from SQL, because it says the guild_id is null
            cache.remove_problem_without_returning(Problem.guild_id, Problem.id) #There will be a recursion error if I normally delete a problem
            #Add the problem again
            cache.add_problem(Problem.guild_id, Problem.id, Problem)   
            return Problem
        problem2 = cls(
            question=problem["question"],
            answer=problem["answer"],
            id = int(problem["id"]),
            guild_id = int(guild_id),
            voters = problem["voters"],
            solvers=problem["solvers"],
            author=problem["author"],
            cache = cache
        )
        return problem2
    def to_dict(self):
        "An alias for convert_to_dict"
        return self.convert_to_dict()
    def convert_to_dict(self):
        """Convert self to a dictionary"""
        warnings.warn("This method has been deprecated. Use from_dict for continued support!", DeprecationWarning)
        return {
            "type": "MathProblem",
            "question": self.question,
            "answer": self.answer,
            "id": str(self.id),
            "guild_id": str(self.guild_id),
            "voters": self.voters,
            "solvers": self.solvers,
            "author": self.author
        }
    def add_voter(self,voter):
        """Adds a voter. Voter must be a nextcord.User object or nextcord.Member object."""
        if not isinstance(voter,nextcord.User) and not isinstance(voter,nextcord.Member):
            raise TypeError("User is not a User object")
        if not self.is_voter(voter):
            self.voters.append(voter.id)
        self.update_self()
    def add_solver(self,solver):
        """Adds a solver. Solver must be a nextcord.User object or nextcord.Member object."""
        if not isinstance(solver,nextcord.User) and not isinstance(solver,nextcord.Member):
            raise TypeError("Solver is not a User object")
        if not self.is_solver(solver):
            self.solvers.append(solver.id)
        self.update_self()
    def get_answer(self):
        "Return my answer. This has been deprecated"
        return self.answer
    def get_answers(self):
        "Return my possible answers"
        return [self.answer, *self.answers] 
    def get_question(self):
        "Return my question."
        return self.question
    def check_answer_and_add_checker(self,answer,potentialSolver):
        "Checks the answer. If it's correct, it adds potentialSolver to the solvers."
        if not isinstance(potentialSolver,nextcord.User) and not isinstance(potentialSolver,nextcord.Member):
            raise TypeError("potentialSolver is not a User object")
        if self.check_answer(answer):
            self.add_solver(potentialSolver)
    def check_answer(self,answer):
        "Checks the answer. Returns True if it's correct and False otherwise."
        return answer in self.get_answers()
    def my_id(self):
        "Returns id & guild_id in a list. id is first and guild_id is second."
        return [self.id, self.guild_id]
    def get_voters(self):
        "Returns self.voters"
        return self.voters
    def get_num_voters(self):
        "Returns the number of solvers."
        return len(self.get_voters())
    def is_voter(self,User):
        "Returns True if user is a voter. False otherwise. User must be a nextcord.User or nextcord.Member object."
        if not isinstance(User,nextcord.User) and not isinstance(User,nextcord.Member):
            raise TypeError("User is not actually a User")
        return User.id in self.get_voters()
    def get_solvers(self):
        "Returns self.solvers"
        return self.solvers
    def is_solver(self,User):
        "Returns True if user is a solver. False otherwise. User must be a nextcord.User or nextcord.Member object."
        if not isinstance(User,nextcord.User) and not isinstance(User,nextcord.Member):
            raise TypeError("User is not actually a User")
        return User.id in self.get_solvers()
    def get_author(self):
        "Returns self.author"
        return self.author
    def is_author(self,User):
        "Returns if the user is the author"
        if not isinstance(User,nextcord.User) and not isinstance(User,nextcord.Member):
            raise TypeError("User is not actually a User")
        return User.id == self.get_author()
    def __eq__(self,other):
        "Return self==other"
        if not isinstance(self, type(other)):
            return False
        try:
            return self.question == other.question and other.answer == self.answer
        except:
            return False
    def __repr__(self):
        "A method that when called, returns a string, that when executed, returns an object that is equal to this one. Also implements repr(self)"
        return f"""problems_module.MathProblem(question={self.question},
        answer = {self.answer}, id = {self.id}, guild_id={self.guild_id},
        voters={self.voters},solvers={self.solvers},author={self.author},cache={None})""" # If I stored the problems, then there would be an infinite loop
    def __str__(self, include_answer = False):
        "Implement str(self)"
        _str = f"""Question: {self.question}, 
        id: {self.id}, 
        guild_id: {self.guild_id}, 
        solvers: {[f'<@{id}>' for id in self.solvers]},
        author: <@{self.author}>"""
        if include_answer:
            _str += f"\nAnswer: {self.answer}"
        return str(_str)
class QuizSubmissionAnswer:
    "A class that represents an answer for a singular problem"
    def __init__(self, answer: str= "", problem_id: int= None,quiz_id: int =-1):
        self.answer = answer
        self.problem_id = problem_id
        self.grade = 0
        self.quiz_id = quiz_id
    def set_grade(self,grade):
        self.grade=grade
    def __str__(self):
        return str(self.answer)
class QuizSubmission:
    "A class that represents someone's submission to a graded quiz"
    def __init__(self,user: nextcord.User, quiz_id):
        self.user_id = user.id
        self.quiz_id = quiz_id
        self.mutable = True
        self.answers = [QuizSubmissionAnswer(problem=question,quiz_id= quiz_id) for question in self.get_my_quiz()]
    @property
    def quiz(self):
        "Return my quiz!"
        return self.get_my_quiz()
    def get_my_quiz(self):
        "Return my Quiz!"
        return get_main_cache().get_quiz(self.quiz_id)
    def set_answer(self,problem_id, Answer) -> None:
        "Set the answer of a quiz problem"
        if not self.mutable:
            raise RuntimeError("This instance is not mutable")
        for answer in self.answers:
            if answer.problem.id == problem_id:
                answer.answer = Answer
    def to_dict(self):
        t = {
            "mutable": self.mutable,
            "quiz_id": self.quiz_id,
            "user_id": self.user_id,
            "answer": []
        }
        for answer in self.answers:
            t["answer"].append({"problem_id": answer.problem.id, "answer": answer.answer})
        return t
    @classmethod
    def from_dict(cls, dict_):
        "Convert a dictionary into a QuizSubmission"
        c = cls(user_id=dict_["user_id"], quiz_id = "quiz_id")
        for answer in dict_["answers"]:
            c.answers.append(QuizSubmissionAnswer(answer["answer"], problem_id= answer["problem_id"]))
        c.mutable = dict_["mutable"]
        return c
    def submit(self) -> True:
        self.mutable = False
        if self in self.quiz.submissions:
            raise QuizAlreadySubmitted
        self.quiz.submissions.append(self)
        return True



class QuizMathProblem(MathProblem):
    "A class that represents a Quiz Math Problem"
    def __init__(self,question,answer,id,author,guild_id="_global", voters=[],solvers=[], cache=None,answers=[],is_written=False,quiz_id=  None, max_score=-1, quiz=None):
        "A method that allows the creation of new QuizMathProblems"
        if not isinstance(quiz. Quiz):
            raise TypeError(f"quiz is of type {quiz.__class.__name}, not Quiz") # Here to help me debug
        
        super().__init__(question,answer,id,author,guild_id,voters,solvers,cache,answers) # 
        self.is_written = False
        if quiz is not None:
          self.quiz_id = quiz.id
        else:
          self.quiz_id = quiz_id
        self.max_score = max_score
        self.min_score = 0
    @property
    def quiz(self):
        "Return my quiz"
        if self.cache is None:
            return None # I don't have a cache to get my quiz from!
        else:
            return self.cache.get_quiz(self.quiz_id)
    def edit(self,question=None,answer=None,id=None,guild_id=None,voters=None,solvers=None,author=None, answers = None,is_written=None, quiz = None, max_score: int = -1):
        "Edit a problem!"
        super().edit(question,answer,id,guild_id,voters,solvers,author,answers)
        if not isinstance(quiz, Quiz):
            raise TypeError(f"quiz is of type {quiz.__class.__name}, not Quiz") # Here to help me debug
        self.quiz = Quiz
        if not isinstance(is_written, bool):
            raise TypeError("is_written is not of type bool")
        self.update_self()
    def to_dict(self):
        return {
            "type": "QuizMathProblem",
            "question": self.question,
            "answer": self.answer,
            "id": str(self.id),
            "guild_id": str(self.guild_id),
            "voters": self.voters,
            "solvers": self.solvers,
            "author": self.author,
            "quiz_id": self.quiz_id,
            "is_written": self.is_written,
            "max_score": self.max_score
        }
    @classmethod
    def from_dict(cls, Dict, cache=None):
        "Convert a dictionary to a QuizProblem. Even though the bot uses SQL, this is used in the from_row method"
        Dict.pop("type")
        return cls(*Dict, cache = cache)
    @classmethod
    def from_row(cls, row, cache=None):
        try:
            voters = pickle.loads(row["voters"])
            _dict = {
                "quiz_id": row["quiz_id"],
                "guild_id": row["guild_id"],
                "voters": row["voters"]
            }
            return cls.from_dict(_dict, cache = cache)
        except BaseException as e:
            traceback.print_exception(type(e), e, e.__traceback, file = sys.stderr) # Log to stderr
            raise MathProblemsModuleException("Oh no... conversion from row failed") from e # Re-raise (which wil log)
    def update_self(self):
        "Update myself"
        if self.cache is not None:
            self.quiz.update_self()
    
        
class Quiz(list): 
    "Essentially a list, so it implements everything that a list does, but it has an additional attribute submissions which is a list of QuizSubmissions"
    def __init__(self, id: str, iter: List[QuizMathProblem], cache = None):
        """Create a new quiz. id is the quiz id and iter is an iterable of QuizMathProblems"""


        #Later, I will need to use 
        super().__init__(iter)
        self._cache = cache
        self._submissions = []
        self._id = id
    def add_submission(self,submission):
        assert isinstance(submission, QuizSubmission)
        submission.mutable = False
        self._submissions.append(submission)
        self.update_self()
    @property
    def submissions(self):
        return self._submissions
    @classmethod
    def from_dict(cls,_dict: dict):
        problemsAsType = []
        submissions = []
        Problems = _dict["problems"]
        for p in Problems:
            problemsAsType.append(QuizMathProblem.from_dict(p))
        problemsAsType.sort(key= lambda problem: problem.id)

        for s in _dict["submissions"]:
            submissions.append(QuizSubmission.from_dict(s))
        c = cls([])
        c.extend(problemsAsType)
        c._submissions = submissions
        c._id = _dict["id"]
        return c
    def to_dict(self):
        "Convert this instance into a Dictionary to be stored in SQL"
        Problems = [problem.to_dict() for problem in self]
        Submissions = [submission.to_dict for submission in self.submissions]
        return {"problems": Problems, "submissions": Submissions, "id": self._id}
    def update_self(self):
        "Update myself in the sqldict"
        self._cache.update_quiz(self._id, self)
class MathProblemCache:
    "A class that stores math problems/quizzes :-)"
    def __init__(self,max_answer_length=100,max_question_limit=250,
    max_guild_problems=125,warnings_or_errors = "warnings",
    db_name: str = "problems_module.db",name="1",
    update_cache_by_default_when_requesting=True,
    use_cached_problems: bool = False):
        "Create a new MathProblemCache. the arguments should be self-explanatory"
        #make_sql_table([], db_name = sql_dict_db_name)
        #make_sql_table([], db_name = "MathProblemCache1.db", table_name="kv_store")
        self.db_name = db_name
        if warnings_or_errors not in ["warnings", "errors"]:
            raise ValueError(f"warnings_or_errors is {warnings_or_errors}, not 'warnings' or 'errors'")
        self.warnings = (warnings_or_errors == "warnings")
        self.use_cached_problems = use_cached_problems
        self._max_answer = max_answer_length
        self._max_question = max_question_limit
        self._guild_limit = max_guild_problems
        asyncio.run(self.initalize_sql_table())
        self.update_cache_by_default_when_requesting=update_cache_by_default_when_requesting
    def _initialize_sql_dict(self):
        self._sql_dict = sqldict.SqlDict(name=f"MathProblemCache1.db",table_name = "kv_store")
        self.quizzes_sql_dict = sqldict.SqlDict(name = "TheQuizStorer", table_name = "quizzes_kv_store")
    async def initialize_sql_table(self):
        async with aiosqlite.connect(self.db_name) as conn:
            cursor = conn.cursor()
            await cursor.execute("""CREATE TABLE IF NOT EXISTS Problems (
                    guild_id INT PRIMARY KEY,
                    problem_id INT PRIMARY KEY NOT NULL ,
                    question TEXT(2000) NOT NULL,
                    answers BLOB NOT NULL, 
                    author INT NOT NULL,
                    voters BLOB NOT NULL,
                    solvers BLOB NOT NULL
                    )""") #Blob types will be compliled with pickle.loads() and pickle.dumps() (they are lists)
                    #author: int = user_id

            await cursor.execute("""CREATE TABLE IF NOT EXISTS quizzes (
                guild_id INT,
                quiz_id INT NOT NULL,
                problem_id INT NOT NULL,
                question TEXT(500) NOT NULL,
                answer BLOB NOT NULL,
                voters BLOB NOT NULL,
                author INT NOT NULL,
                solvers INT NOT NULL
            )""")
            #Used for quizzes
             # answer: Blob (a list)
            #voters: Blob (a list)
            #solvers: Blob (a list)
            #submissions: Blob (a dictionary)
            await cursor.execute("""CREATE TABLE IF NOT EXISTS quiz_submissions (
                guild_id INT,
                quiz_id INT NOT NULL,
                submissions BLOB NOT NULL
                )""") #as dictionary
            #Used to store submissions!
            
            await conn.commit() #Otherwise, when this closes, the database just reverted!

    @property
    def max_answer_length(self):
        return self._max_answer
    @property
    def max_question_length(self):
        return self._max_question
    @property
    def max_guild_problems(self):
        return self._guild_limit



    def convert_to_dict(self):
        "A method that converts self to a dictionary (not used, will probably be removed soon)"
        e = {}
        self.update_cache()

        for guild_id in self.guild_ids:
            e[guild_id] = {}
            for Problem in self.guild_problems[guild_id]:
                e[guild_id][Problem.id] = Problem.to_dict()
        return e
    def convert_dict_to_math_problem(self,problem):
        "Convert a dictionary into a math problem. It must be in the expected format. (Overriden by from_dict, but still used) Possibly not used due to SQL"
        if __debug__:
            return MathProblem.from_dict(problem, cache=self)
        try:
            assert isinstance(problem,dict)
        except AssertionError:
            raise TypeError("problem is not actually a Dictionary")
        guild_id = problem["guild_id"]
        if guild_id == "_global":
            guild_id = "_global"
        else:
            guild_id = int(guild_id)
        problem2 = self(
            question=problem["question"],
            answer=problem["answer"],
            id = int(problem["id"]),
            guild_id = guild_id,
            voters = problem["voters"],
            solvers=problem["solvers"],
            author=problem["author"]
        )
        return problem2
    async def update_cache(self):
        "Method revamped! This method updates the cache of the guilds, the guild problems, and the cache of the global problems. Takes O(N) time"
        guild_problems = {}
        guild_ids = []
        global_problems = {}

        async with aiosqlite.connect(self.db_name) as conn:
            conn.row_factory = dict_factory
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM problems")

            for row in cursor:
                Problem = MathProblem.from_row(row, cache=copy(self))
                if Problem.guild_id not in guild_ids: # Similar logic: Make sure it's there!   
                    guild_ids.append(Problem.guild_id)
                    guild_problems[Problem.guild_id] = {} #For quick, cached access?
                try:
                    guild_problems[Problem.guild_id][Problem.id] = Problem
                except BaseException as e:
                    raise SQLException("Uh oh..... oh no..... uh..... please help! For some reason, the cache couldn't be updated") from e
                    


        try:
            global_problems = deepcopy(guild_problems["_global"]) #contention deepcopying more :-)           
        except KeyError as exc: # No global problems yet
            global_problems = {}
        self.guild_problems = deepcopy(guild_problems) # More deep-copying (so it refers to a different object)
        self.guild_ids = deepcopy(guild_ids)
        self.global_problems = deepcopy(global_problems)
    async def get_problem(self,guild_id: int, problem_id: int):
        "Gets the problem with this guild id and problem id"

        
        if not isinstance(guild_id, int):
            if self.warnings:
                warnings.warn("guild_id is not a integer!", category=RuntimeWarning)
            else:
                raise TypeError("guild_id isn't an integer and this will cause issues in SQL!")
        if not isinstance(problem_id,int):
            if self.warnings:
                warnings.warn("problem_id is not a integer",category=RuntimeWarning)
            else:
                raise TypeError("problem_id is not a integer")
        if self.use_cached_problems:
            if self.update_cache_by_default_when_requesting:
                await self.update_cache()
            return self.guild_problems[guild_id][problem_id]
        else:
            #Otherwise, use SQL to get the problem!
            async with aiosqlite.connect(self.db_name) as conn:
                conn.row_factory = dict_factory
                cursor = conn.cursor()
                await cursor.execute("SELECT * from problems WHERE guild_id = ? AND problem_id = ?", (guild_id, problem_id))
                row = await cursor.fetchone()
                await conn.commit()
                return MathProblem.from_row(row, cache=copy(self))
            
            

                


    async def get_guild_problems(self,Guild):
        """Gets the guild problems! Guild must be a Guild object. If you are trying to get global problems, use get_global_problems."""
        if self.update_cache_by_default_when_requesting:
            await self.update_cache()
        try:
            return self.guild_problems[Guild.id]
        except KeyError:
            return {}
        
    def get_global_problems(self):
        "Returns global problems"
        if self.update_cache_by_default_when_requesting:
            self.update_cache()
        return self.global_problems
    def add_empty_guild(self,Guild):
        "Adds an dictionary that is empty for the guild. Guild must be a nextcord.Guild object"
        pass #No longer needed
        #if not isinstance(Guild, nextcord.Guild):
        #    raise TypeError("Guild is not actually a Guild")
        #try:
        #    if self._dict[str(Guild.id)] != {}:
        #        raise GuildAlreadyExistsException
        #except KeyError:
        #    self._dict[str(Guild.id)] = {}
        #    
        #self._dict[Guild.id] = {}
    def add_problem(self,guild_id,problem_id,Problem):
        "Adds a problem and returns the added MathProblem"
        if not isinstance(guild_id,str):
            if self.warnings:
                warnings.warn("guild_id is not a string.... this may cause an exception")
            else:
                raise TypeError("guild_id is not a string.")
        if not isinstance(problem_id,str):
            if self.warnings:
                warnings.warn("problem_id is not a string.... this may cause an exception")
            else:
                raise TypeError("problem_id is not a string.")
        try:
            if guild_id == "_global":
                pass
            elif len(self.guild_problems[guild_id]) > self.max_guild_problems:
                raise TooManyProblems(f"There are already {self.max_guild_problems} problems!")
        except KeyError:
            pass
        if not isinstance(Problem,(MathProblem, dict)):
            raise TypeError("Problem is not a valid MathProblem object.")
        if isinstance(Problem,MathProblem):
            try:
                Problem = Problem.convert_to_dict()
            except Exception:
                raise MathProblemsModuleException("Not a valid problem!")
        else:
            try: # make sure this is a valid problem
                MathProblem.from_dict(Problem, cache = self) # If this is invaid, then there will be a keyerror
            except KeyError:
                raise MathProblemsModuleException("Problem is not a valid problem")
        try:
            if self.get_problem(guild_id,problem_id) is not None:
                raise MathProblemsModuleException("Problem already exists")
        except BaseException as e:
            if not isinstance(e,KeyError):
                raise RuntimeError("Something bad happened... please report this! And maybe try to fix it?") from e
            
        self._sql_dict[f"{guild_id}:{problem_id}"] = Problem.to_dict()
#        if guild_id != 'null':
#            try:
#                if self._dict[guild_id] != {}:
#                    raise GuildAlreadyExistsException
#                else:
#                    self._dict[guild_id] = {}
#            except:
#                self._dict[guild_id] = {}
        
        return Problem
    def remove_problem(self,guild_id,problem_id):
        "Removes a problem. Returns the deleted problem"
        if not isinstance(guild_id, str):
            if self.warnings:
                warnings.warn("guild_id is not a string. There might be an error...", Warning)
            else:
                raise TypeError("guild_id is not a string")

        Problem = self.get_problem(guild_id,problem_id)
        with sqlite3.connect(self.sql_dict.name) as connection: # The sqldict does not implement deletion, so I have to do sql magic
            connection.cursor().execute(f"DELETE FROM {self._sql_dict.__tablename__} WHERE key = \"{str(guild_id)}:{str(problem_id)}")
            connection.commit()

        return Problem
    def remove_problem_without_returning(self, guild_id, problem_id):
        "Remove a problem without returning"
        key = f"{guild_id}:{problem_id}"
        with sqlite3.connect(self._sql_dict.name) as connection:
            connection.cursor().execute("DELETE FROM kv_store WHERE Key = ?", (key,)) # Very weird syntax, but otherwise SQLite sees it as a list of characters instead of a string
            connection.commit()
            
    def remove_duplicate_problems(self):
        "Deletes duplicate problems"
        problems_seen_before = []
        for key in self._sql_dict.keys():
            p = MathProblem.from_dict(_dict=self._sql_dict[key])
            if p in problems_seen_before:
                del self._sql_dict[key]
        #problemsDeleted = 0
        #c = deepcopy(self._dict)
        #d = deepcopy(c)
        #for g1 in self._dict.keys():
        #    for p1 in self._dict[g1].keys():
        #        for g2 in c.keys():
        #            for p3 in c[g2].keys():
        #                if self._dict[g1][p1] == c[g2][p3] and not (g1 == g2 and p1 != p3):
        #                    try:
        #                        del d[g1][p1]
        #                    except KeyError:
        #                        continue
        #                    problemsDeleted += 1
    def get_guilds(self, bot: nextcord.ext.commands.Bot = None) -> List[Union[int, Optional[nextcord.Guild]]]:
        "Get the guilds (due to using sql, it must return the guild id, bot is needed to return guilds. takes O(n) time"
        try:
            assert bot == None or isinstance(bot, nextcord.ext.commands.Bot)
        except:
            raise AssertionError("bot isn't a bot!")

        if self.update_cache_by_default_when_requesting:
            self.update_cache()
        
        if bot is not None:
            self._guilds = []
            for guild_id in self.guild_ids:
                guild = bot.get_guild(guild_id)
                if guild is None:
                    if self.warnings:
                        warnings.warn("guild is None")
                    else:
                        raise RuntimeError(f"Guild not found (id: {guild_id}) :-(")
                else:
                    self._guilds.append(guild)
            return self._guilds

        return self.guild_ids
    def add_quiz(self,quiz: Quiz) -> Quiz:
        "Add a quiz"
        self.quizzes_sql_dict[f"Quiz:{quiz.id}"] = quiz.to_dict()
    def __str__(self):
        raise NotImplementedError
    def get_quiz(self, quiz_id: int) -> Optional[Quiz]:
        "Get the quiz with the id specified. Returns None if not found"
        assert isinstance(quiz_id, int)
        return Quiz.from_dict(self.quizzes_sql_dict[f"Quiz:{quiz_id}"]) # Convert the result to a quiz (result is getting the Quiz dictionary from the quizzes_sql_dict)
    def update_problem(self,guild_id, problem_id, new: MathProblem) -> None:
        "Update the problem stored with the given guild id and problem id"
        assert isinstance(guild_id, str)
        assert isinstance(problem_id, str)
        assert isinstance(new, MathProblem) and not isinstance(new, QuizMathProblem)
        self._sqldict[f"{guild_id}:{problem_id}"] = new.to_dict()
    def update_quiz(self, quiz_id, new) -> None:
        "Update the quiz with the id given"
        assert isinstance(quiz_id, str)
        assert isinstance(new, Quiz)
        self.quizzes_sql_dict[f"Quiz:{quiz_id}"] = new.to_dict()
    async def delete_quiz(self, quiz_id, guild_id):
        "Delete a quiz!"
        async with aiosqlite.connect(self._sql_dict_db_name) as conn:
            cursor = conn.cursor()
            await cursor.execute("DELETE FROM quizzes WHERE quiz_id = ? AND guild_id = ?", (quiz_id, guild_id,))
            await conn.commit()
main_cache = MathProblemCache(max_answer_length=100,max_question_limit=250,max_guild_problems=125,warnings_or_errors="errors")
def get_main_cache():
    "Returns the main cache."
    return main_cache
