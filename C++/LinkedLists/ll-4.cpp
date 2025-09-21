// Linked list with iterators. No need to access the nodes of the list directly

#include <iostream>
using namespace std;

class Node {
public:
	Node(int d, Node *n = NULL, Node *p = NULL) 
		: data(d), next(n), prev(p) {}

	int data;
	Node *get_next() { return next; }
	Node *get_prev() { return prev; }
	
	friend class List;
private:
	Node *next;
	Node *prev;
};

class Iterator {
public:
	Iterator(Node* n) { current = n; }
	int next_element() { 
		int to_be_returned = current->data;
		current = current->get_next();
		return to_be_returned;
	}
	bool has_more_elements() {
		return current != NULL;
	}
private:
	Node *current;
};

class List {
public:
	List();
	~List();
	void print();
	void push_front(int x);
	void push_back(int x);
	Iterator get_iterator() {
		return Iterator(_head);
	}
private:
	Node* _head;
	Node* _last;
};

List::List() {
	_head = NULL;
	_last = NULL;
}

void List::print() {
	for (Node* p = _head; p != NULL; p = p->next) {
		cout << p->data << ' ';
	}
}

void List::push_front(int x) {
	Node *new_node = new Node(x);
	new_node->next = _head;
	if (_head != NULL)
		_head->prev = new_node;
	_head = new_node;
	if (_last == NULL)
		_last = new_node;
}

void List::push_back(int x) {
	if (_head == NULL)
		push_front(x);
	else {
		Node *new_node = new Node(x);
		new_node->prev = _last;
		_last->next = new_node;
		_last = new_node;
	}
}

List::~List() {
	Node *p = _head;
	while (p != NULL) {
		Node *q = p;
		p = p->next;
		delete q;
	}
	_head = NULL;
}

int main() {
	List l;
	
	l.push_back(86);
	l.push_front(43);
	l.push_front(12);
	
	l.print();
	cout << endl;

	// head() is removed. The threats are no more!
	// l.head()->next = NULL;
	// delete l.head();

	int sum = 0;
	
	Iterator it = l.get_iterator();
	while (it.has_more_elements())
		sum += it.next_element();
		
		
	cout << sum << endl;
}


























