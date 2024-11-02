import turtle
def draw_heart(size,color1,color2):
    turtle.speed(1)    
    turtle.color((1.2,1.3,1.4))    
    turtle.begin_fill()    
    turtle.left(140)    
    turtle.forward(size)    
    for _ in range(200):
        turtle.right(1)        
        turtle.forward(size*3.14/180/2)        

    turtle.left(120)    
    for _ in range(200):
        turtle.right(1)        
        turtle.forward(size*3.14/180/2)        

    turtle.forward(size)    
    turtle.end_fill()    

def draw_star(size,color):
    turtle.color(color)    
    turtle.begin_fill()    
    for _ in range(5):
        turtle.forward(size)        
        turtle.right(144)        

    turtle.end_fill()    

def draw_spiral(length,angle,color):
    turtle.color(color)    
    turtle.speed(5)    
    for i in range(length):
        if (i/20)-int(i/20)==0:
            turtle.right(angle)            

        else:
            turtle.forward(i/2)            
            turtle.right(angle)            



turtle.setpos((100))
draw_heart(100,color1="red",color2="pink")
turtle.penup()
turtle.goto(-50,-100)
turtle.pendown()
draw_star(150,"yellow")
turtle.penup()
turtle.goto(200,200)
turtle.pendown()
draw_spiral(100,45,"blue")
turtle.hideturtle()
turtle.done()
