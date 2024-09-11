import easyocr
import cv2
import json
import numpy as np
reader = easyocr.Reader(['en','fr'])
# @brief Filter the data read in Text to extract the informations from the CIN
# @params r: the numbers of rows in the original image
# @params c: the number of columns in it
def scanCin(Text,r,c):
    Texts=[]
    temp=[]
    for i in Text:
        if len(i[1]) >2:
            temp.append(i)
    Text=temp
    for i in Text:
        if is_text(i[1],True):
            Texts.append(i)
    Dates=[]
    for i in Text:
        j=i[1]
        if is_date(j):
            Dates.append(i)
    CIN=[]
    for i in Text:
        j=i[1]
        if is_valid_cin(j):
            CIN.append(i)
    Validation_date=[]
    for i in Text:
        j=i[1]
        if is_valid_validation_date(j):
            Validation_date.append(i)
    Ans=dict()
    Ans['Prenom']=[[[0,0] for i in range(4)],"",0]
    Ans['Nom']=[[[0,0] for i in range(4)],"",0]
    Ans['Naissance']=[[[0,0] for i in range(4)],"",0]
    Ans["Numero"]=[[[0,0] for i in range(4)],"",0]
    Ans['Validation']=[[[0,0] for i in range(4)],"",0]
    for i in Texts:
        Ans['Prenom']=compare_candidates_first_name(Ans['Prenom'],i,r,c)
    if Ans['Prenom'][2] !=0:
        Texts.pop(Texts.index(Ans['Prenom']))
    Ans['Prenom']=[Ans['Prenom'][1],Ans['Prenom'][2]]
    for i in Texts:
        Ans['Nom']=compare_Candidates_last_name(Ans['Nom'],i,r,c)
    Ans['Nom']=[Ans['Nom'][1],Ans['Nom'][2]]
    for i in Dates:
        Ans['Naissance']=compare_candidates_birthday(Ans['Naissance'],i,r,c)
    Ans['Naissance']=[Ans['Naissance'][1],Ans['Naissance'][2]]
    for i in CIN:
        Ans['Numero']=compare_cin_number(Ans['Numero'],i,r,c)
    Ans['Numero']=[Ans['Numero'][1],Ans['Numero'][2]]
    for i in Validation_date:
        Ans['Validation']=compare_validation_date(Ans['Validation'],i,r,c)
    temp=Ans['Validation'][1]
    if temp!="":
        for i in range(len(temp)-9):
            if is_date(temp[i:i+10]):
                temp=temp[i:i+10]
                break
    Ans['Validation']=[temp,-1]
    return Ans
# @brief Filter the data read in Text to extract the informations of the merchant
# @params Text: Is an array of [[[x,y],[x,y],[x,y],[x,y]],text,precision] where the [x,y] describe the 4-gone containing the text, "text" is the string read and "precision" is the approximated probability of the text being read correctly!
def scanMerchant(Text):
    for i in range(len(Text)):
        Text[i]=[Text[i][0],Text[i][1],Text[i][2]]
        Text[i][0]=Get_Rectangle(Text[i][0])
    Text.sort(key= lambda x: x[0][-1])
    Lines=extract_lines(Text)
    Lines=filer_lines(Lines)
    Closest=locate_fields(Lines)
    ANS=dict()
    curr=0
    for i in range(Closest[0][0],len(Lines)):
        while curr+1<len(Closest) and i>=Closest[curr+1][0]:
            curr+=1
        if curr+1>=len(Closest):
            break
        if i==Closest[curr][0]:
            ANS[Fields[curr]]=[Lines[i][1][Closest[curr][1][1]:],Lines[i][2]]
        else:
            ANS[Fields[curr]]=[ANS[Fields[curr]][0]+" "+Lines[i][1],ANS[Fields[curr]][1]*Lines[i][2]]
    return ANS
# @brief scan a standard image and return JSON containing the informations included
# @params Type: must equals "CIN" if the image is of a CIN, or "MERCHANT" if it correspand to a merchant
# @params Image: Contains the image in a cv2 form
def scan(Type="",Image=[]):
    Type=Type.upper()
    Text=reader.readtext(Image)
    r,c,_=Image.shape
    if Type=="CIN":
        return json.dumps(scanCin(Text,r,c))
    if Type=="MERCHANT":
        return json.dumps(scanMerchant(Text))
    return json.dumps({})


#Functions and constants used for CIN scan:
P_fn=[0.4,0]
P_ln=[0.4,0]
P_bd=[0.6,0.4]
P_CN=[0.09,0.89]
P_Val=[0.56,0.87]
def is_number(Text):
    Numbers=['0','1','2','3','4','5','6','7','8','9']
    for j in Text:
        if j not in Numbers:
            return False
    return True
def is_valid_date(date):
    d,m,y=int(date[:2]),int(date[3:5]),int(date[6:])
    if d>31 or d<1 or m>12 or m<1 or y<0:
        return False
    if d < 29:
        return True
    if m==2 :
        if d!=29:
            return False
        if y%400==0 or (y%100!=0 and y%4==0):
            return True
        return False
    if d==30 or (m+m//8)%2==1:
        return True
    return False
def is_date(Text):
    if Text[2]=='.' and Text[5]=='.':
        Temp=Text[:2]+Text[3:5]+Text[6:10]
        if is_number(Temp):
            return is_valid_date(Text)
    return 0
def is_valid_validation_date(Text):
    S=Text.split()
    Text=""
    for i in S:
        Text+=i
    for i in range(len(Text)-9):
            if is_date(Text[i:i+10]):
                return True
    return False
def is_text(Text,Maj:bool ):
    for k in Text:
        if k!=' ' :
            if  ord(k) not in range(ord('A'),ord('Z')+1):
                if Maj  or ord(k) not in range(ord('a'),ord('z')+1):
                    return False
    return True
def is_valid_cin(Text):
    if len(Text)<6:
        return False
    return (is_text(Text[:1],True) and is_number(Text[2:]) ) and(is_text(Text[1:2],True) or is_number(Text[1:2]))
 
def get_top_left_corner(I,r,c):
    return [min(I[0][j][0] for j in range(4))/c,min(I[0][j][1] for j in range(4))/r]
def compare_candidates_first_name(I1,I2,r,c):
    if I1[1]=="":
        if I2[1]=="":
            return I1
        return compare_candidates_first_name(I2,I1,r,c)
    Dep= I1[1].split()[0]
    P1,P2=get_top_left_corner(I1,r,c),get_top_left_corner(I2,r,c)
    if Dep == "ROYAUME" or Dep=="CARTE":
        return I2
    if P1[0] <0.2 or P1[0]>0.5 or P1[1]>0.4 or P1[1]<0.1:
        return I2
    if I2[1]=="":
        return I1
    Dep= I2[1].split()[0]
    if Dep == "ROYAUME" or Dep=="CARTE":
        return I1
    if P2[0] <0.2 or P2[0]>0.5 or P2[1]>0.5 or P2[1]<0.1:
        return I1
    diff = abs(P1[0]-P_fn[0])+abs(P1[1]-P_fn[1])-abs(P2[0]-P_fn[0])-abs(P2[1]-P_fn[1])
    if diff>0:
        return I2
    return I1
def compare_Candidates_last_name(I1,I2,r,c):
    if I1[1]=="":
        if I2[1]=="":
            return I1
        return compare_Candidates_last_name(I2,I1,r,c)
    Dep= I1[1].split()[0]
    if Dep == "ROYAUME" or Dep=="CARTE":
        return I2
    P1,P2=get_top_left_corner(I1,r,c),get_top_left_corner(I2,r,c)
    if P1[0] <0.2 or P1[0]>0.5 or P1[1]>0.5 or P1[1]<0.2:
        return I2
    if I2[1]=="":
        return I1
    Dep= I2[1].split()[0]
    if Dep == "ROYAUME" or Dep=="CARTE":
        return I1
    if P2[0] <0.2 or P2[0]>0.5 or P2[1]>0.5 or P2[1]<0.2:
        return I1
    diff = abs(P1[0]-P_ln[0])+abs(P1[1]-P_ln[1])-abs(P2[0]-P_ln[0])-abs(P2[1]-P_ln[1])
    if diff>0:
        return I2
    return I1
def compare_candidates_birthday(I1,I2,r,c):
    if I1[1]=="":
        if I2[1]=="":
            return I1
        return compare_candidates_birthday(I2,I1,r,c)
    P1,P2=get_top_left_corner(I1,r,c),get_top_left_corner(I2,r,c)
    if P1[0] <0.4 or P1[1]>0.75 or P1[1]<0.2 or P1[1]>0.6:
        return I2
    if I2[1]=="":
        return I1
    if P2[0] <0.4 or P2[1]>0.75 or P2[1]<0.2 or P1[1]>0.6:
        return I1
    diff = abs(P1[0]-P_bd[0])+abs(P1[1]-P_bd[1])-abs(P2[0]-P_bd[0])-abs(P2[1]-P_bd[1])
    if diff>0:
        return I2
    return I1
def compare_cin_number(I1,I2,r,c):
    if I1[1]=="":
        if I2[1]=="":
            return I1
        return compare_cin_number(I2,I1,r,c)
    P1,P2=get_top_left_corner(I1,r,c),get_top_left_corner(I2,r,c)
    if P1[0] >0.3 or P1[1]<0.7 :
        return I2
    if I2[1]=="":
        return I1
    if P2[0] >0.3 or P2[1]<0.7 :
        return I1
    diff = abs(P1[0]-P_CN[0])+abs(P1[1]-P_CN[1])-abs(P2[0]-P_CN[0])-abs(P2[1]-P_CN[1])
    if diff>0:
        return I2
    return I1
def compare_validation_date(I1,I2,r,c):
    if I1[1]=="":
        if I2[1]=="":
            return I1
        return compare_validation_date(I2,I1,r,c)
    P1,P2=get_top_left_corner(I1,r,c),get_top_left_corner(I2,r,c)
    if P1[0] <0.4 or P1[1]<0.7 :
        return I2
    if I2[1]=="" or P2[0] <0.4 or P2[1]<0.7 :
        return I1
    diff = abs(P1[0]-P_Val[0])+abs(P1[1]-P_Val[1])-abs(P2[0]-P_Val[0])-abs(P2[1]-P_Val[1])
    if diff>0:
        return I2
    return I1
#Functions and constants used for Merchant scan
Fields=['-Company name:', '-Company name (if applicable):', '-Legal form:', '-Creation date:', '-Head office address:','-Nature of activity:',
             '-Capital:', '-RC N%:', '-Patent:', '-IF:', '-ICE:', '-Phone number:', '-City and country:', '-Name of legal representative:',
             '-Payment notification email:', '-Email notification of transaction statements:', 'Project contact email:','ll.Buisiness information:']
def Get_Rectangle(I):
    return [min(j[0]for j in I),min(j[1]for j in I),max(j[0]for j in I),max(j[1]for j in I)]

def Same_line(I1,I2):
    A,B=I1[0],I2[0]
    mid1,mid2=(A[-1]+A[1])/2,(B[-1]+B[1])/2
    return  mid1<B[-1] and mid2<A[-1]

def Merge_Line(L,max_diff):
    def Merge_two(X,Y):
        Z=[min(X[0][0],Y[0][0]),min(X[0][1],Y[0][1]),max(X[0][2],Y[0][2]),max(X[0][3],Y[0][3])]
        T=X[1]+" "+Y[1]
        P=X[2]*Y[2]
        return [Z,T,P]
    if len(L)==0:
        return []
    L.sort(key=lambda x: x[0][0])
    Ans=[L[0]]
    for i in range(1,len(L)):
        if L[i][0][0]-Ans[-1][0][2]>max_diff and max_diff!=-1:
            Ans.append(L[i])
        else:
            Ans[-1]=Merge_two(Ans[-1],L[i])
    return Ans

def extract_lines(Text):
        Lines=[]
        for i in Text:
            if len(Lines)==0:
                Lines.append([i])
                continue
            if Same_line(Lines[-1][-1],i):
                Lines[-1].append(i)
            else:
                Lines.append([i])
        return Lines

def filer_lines(Lines):
        temp=[]
        for i in Lines:
            t=Merge_Line(i,max_diff=(i[0][0][3]-i[0][0][1])*10)
            while len(t)>len(temp):
                temp.append([])
            for i in range(len(t)):
                temp[i].append(t[i])
        for i in range(1,len(temp)):
            temp[0]+=temp[i]
        return temp[0]

def locate_fields(Lines):
        Closest=[]
        la=0
        for i in Fields:
            Closest.append([la,[10**8,-1]])
            for j in range(la,len(Lines)):
                t=Distance(i,Lines[j][1])
                if t[0] < Closest[-1][1][0]:
                    Closest[-1]=[j,t]
            la=Closest[-1][0]+1
        return Closest

def Distance(S1,S2):
    n,m=len(S1),len(S2)
    dp=[[max(i,j) for j in range(m+1)]for i in range(n+1)]
    dp[0][0]=0
    for i in range(1,n+1):
        for j in range(1,m+1):
            dp[i][j]=1+min(dp[i-1][j],dp[i][j-1],dp[i-1][j-1])
            for k in range(1,i+1):
                if S1[k-1]==S2[j-1]:
                    dp[i][j]=min(dp[i][j],dp[k-1][j-1]+i-k)
            for k in range(1,j+1):
                if S1[i-1]==S2[k-1]:
                    dp[i][j]=min(dp[i][j],dp[i-1][k-1]+j-k)
    Ind=0
    for j in range(m+1):
        if dp[n][j]<=dp[n][Ind]:
            Ind=j
    return [dp[n][Ind],Ind]