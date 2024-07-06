#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

// Definición de la estructura de un elemento
typedef struct Item {
    char* key;
    void* value;
    struct Item* next;
} Item;

// Definición de la estructura del objeto
typedef struct Object {
    Item* head;
    Item* tail;
} Object;

// Función para añadir un elemento
void addItem (Object* obj, char* key, void* value ){
    Item* newItem = malloc(sizeof(Item));
    newItem->value = value;
    newItem->key = strdup(key);
    newItem->next = NULL;
    
    if (obj->head == NULL) {
        obj->head = newItem;
        obj->tail = newItem;
    } else {
        obj->tail->next = newItem;
        obj->tail = newItem;
    }
}

// Función para obtener el valor de un elemento
void* getItemValue(Object obj, char* key) {
    Item* current = obj.head;
    while (current != NULL) {
        if (strcmp(current->key, key) == 0) {
            return current->value;
        }
        current = current->next;
    }
    return NULL;
}

// Funcion para crear un nuevo objeto 
Object createObject(){
    Object* obj = malloc(sizeof(Object));
    Item* itemHead = malloc(sizeof(Item));
    Item* itemTail = malloc(sizeof(Item));

    obj->head = itemHead;
    obj->tail = itemTail;

    return *obj;
}

// Funcion que evalua un Object que representa a un Bool
bool evaluate_condition(Object condition){
    return getItemValue(condition, "value");
}

// Funcion que devuelve la expresion asociada a la condicion que se cumple
Object conditionalExpr(Object* conditions, Object* expressions, int length, Object default_){
    for (size_t i = 0; i < length; i++)
    {
        if(evaluate_condition(conditions[i])){
            return expressions[i];
        }
    }
    
    return default_;
}

















































/////////////////////////////////////////////////////////////
// Función para obtener un elemento
Item* getItem(Object* obj, char* key) {
    if(obj == NULL)
        throwError("Null Reference");

    Item* current = obj->head;
    while (current != NULL) {
        if (strcmp(current->key, key) == 0) {
            return current;
        }
        current = current->next;
    }
    return NULL;
}

// Función para reemplazar el valor de un elemento
void replaceItem(Object* obj, char* key, void* value) {
    if(obj == NULL)
        throwError("Null Reference");

    Item* item = getItem(obj, key);
    if (item == NULL)
        throwError("Item Not Found");

    item->value = value;
}


// Función para eliminar un elemento
void removeItem(Object* obj, char* key) {
    if(obj == NULL)
        throwError("Null Reference");

    Item* current = obj->head;
    Item* previous = NULL;

    while (current != NULL) {
        if (strcmp(current->key, key) == 0) {
            if (previous == NULL) {
                obj->head = current->next;
            } else {
                previous->next = current->next;
            }
            free(current->key);
            free(current);
            return;
        }
        previous = current;
        current = current->next;
    }
    throwError("Item Not Found");
}
/////////////////////////////////////////////////////////




