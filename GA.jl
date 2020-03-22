using Printf
using Statistics
using Random
using TickTock

function input(prompt::String="")::String
    print(prompt)
    return chomp(readline(stdin))
end

function buildpop(Targetphrase, popsize)
    slength = length(Targetphrase)
    CA = Array{String}(undef,popsize)
    for i = 1:popsize
        CA[i] = randstring(slength)
    end
    return CA
end

function calcfit(Targetphrase, PopCA, popsize)
    fitvec = zeros(popsize)
    slength = length(Targetphrase)
    i = 1;
    tempvec = Array{Bool}(undef,slength)
    
    for n in PopCA
        k = 1;
        for j in n
        tempvec[k] = j == Targetphrase[k]
        k = k+1;
        end
        fitsc = count(tempvec)/slength
        fitvec[i] = fitsc
        i = i+1;
    end
    return fitvec
end

function buildmp(MF,FitnessVec, popsize)
    MP = zeros(0)
    for i = 1:popsize
        tickets = ceil(Int,FitnessVec[i] * MF)
        if tickets == 0
            tickets = 1
        end
        for j = 1:tickets
            append!(MP,i)
        end
    end
    return MP
end

function breed(MP,PopCA, Targetfit)
    slength = length(Targetfit)
    MPlength = length(MP)
    parent1 = rand(MP)
    parent2 = rand(MP)
    while parent1 == parent2
        parent2 = rand(MP)
    end
    parent1 = PopCA[convert(Int,parent1)]
    parent2 = PopCA[convert(Int,parent2)]
    splitln = rand(1:slength)
    parent1 = parent1[1:splitln]
    parent2 = parent2[splitln+1:end]
    child = parent1*parent2
    return child
end

function mutate(child, Mutfac, Targetfit)
    slength = length(Targetfit)
    chance = rand(0:100)::Int
    amount = rand(1:slength)::Int
    for i = 1:amount
        mutposition = convert(Int,rand(1:slength))
        if chance <= Mutfac
            newchar = randstring(1)
            child = collect(child)
            tofind = child[mutposition]
            child = replace(child,tofind => newchar)
            child = join(child)
        end
    end
    return child
end

function main()
    #Initialize Script
    Targetfit = input("Choose a Target String: ")
    MF = parse(Int,input("Choose a Mating Factor: "))
    Mutfac = parse(Int,input("Choose a Mutation Factor (%): "))
    maxgen = parse(Int,input("Choose the Maximum Number of Generations to Simulate: "))
    popsize = parse(Int,input("Choose the Population Size: "))
    G = 1;

    tick();                                 #Time how long the algorithm takes
        #Initialize the Population
        PopCA = buildpop(Targetfit,popsize)
        Fitvec = calcfit(Targetfit,PopCA,popsize)
        maxfit = maximum(Fitvec)
        maxfitvec = [maxfit]
        maxindex = argmax(Fitvec)
        @printf("Max Fitness Value (Generation %d): %.4f %s \n",G,maxfit,PopCA[maxindex])

        #Begin to Breed new Generations
        while maxfit<1 && G != maxgen
            G = G+1;
            MP = buildmp(MF,Fitvec,popsize)
            newpool = Array{String}(undef,popsize)
            for i = 1:popsize
                Child = breed(MP,PopCA,Targetfit)
                newpool[i] = mutate(Child,Mutfac,Targetfit)
            end
            PopCA = newpool
            Fitvec = calcfit(Targetfit,PopCA,popsize)
            maxfit = maximum(Fitvec)
            append!(maxfitvec,maxfit)
            maxindex = argmax(Fitvec)
            @printf("Max Fitness Value (Generation %d): %.4f %s \n",G,maxfit,PopCA[maxindex])
        end
        comptime = tok();
        if G < maxgen
            @printf("Target Achieved!\nMax Fitness Value (Generation %d): %.4f %s\n",G,maxfit,PopCA[maxindex])
            @printf("Total Time Elapsed: %.4f seconds",comptime)
        else
            @printf("Maximum Generations Reached!\nMax Fitness Value (Generation %d): %.4f %s\n",G,maxfit,PopCA[maxindex])
            @printf("Total Time Elapsed: %.4f seconds",comptime)
        end
return
end

