
# coding: utf-8

# In[1]:

from celery import Celery


# In[2]:

app = Celery('tasks', backend="redis://localhost:6379/0", broker='redis://localhost:6379/0')


# In[3]:

@app.task
def add(x, y):
    return x+y

