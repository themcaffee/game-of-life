import hashlib
import random

import copy


class Genome:
    def __init__(self, organism_id=0, geneparam=None, mom_id=0, dad_id=0):
        if geneparam and (mom_id == 0 or dad_id == 0):
            raise Exception("geneparam provided without mom_id or dad_id")

        self.organism_id = organism_id
        self.mom_id = mom_id
        self.dad_id = dad_id
        self.all_possible_genes = {
            'activation': ['relu', 'elu', 'tanh', 'sigmoid', 'hard_sigmoid', 'softplus', 'linear'],
            'optimizer': ['rmsprop', 'adam', 'sgd', 'adagrad', 'adadelta', 'adamax', 'nadam'],
            'nb_neurons': list(range(2, 48)),
            'nb_layers': list(range(2, 5))
        }

        self.layer_genes = dict(self.all_possible_genes)
        del self.layer_genes['nb_layers']
        del self.layer_genes['optimizer']

        if not geneparam:
            self.set_genes_random()
        else:
            self.set_genes_to(geneparam)

    def update_hash(self):
        """
        Refesh each genome's unique hash - needs to run after any genome changes.
        """
        genh = str(self.geneparam['optimizer'])
        for layer in self.geneparam['layers']:
            genh += str(layer['nb_neurons']) + layer['activation']

        self.hash = hashlib.md5(genh.encode("UTF-8")).hexdigest()

    def set_genes_random(self):
        """Create a random genome."""
        # This gene has no parents
        self.mom_id = 0
        self.dad_id = 0
        self.geneparam = {}

        # random optimizer
        self.geneparam['optimizer'] = random.choice(self.all_possible_genes['optimizer'])

        # random number and parameters of layers
        num_layers = random.choice(self.all_possible_genes['nb_layers'])
        layers = []
        for i in range(num_layers):
            new_layer = {}
            for param in self.layer_genes:
                new_layer[param] = random.choice(self.all_possible_genes[param])
            layers.append(new_layer)
        self.geneparam['layers'] = layers

        self.update_hash()

    def mutate_one_gene(self):
        """Randomly mutate one gene in the genome.
        Args:
            network (dict): The genome parameters to mutate
        Returns:
            (Genome): A randomly mutated genome object
        """
        # The number of possible choices. optimizer + num layers * num possible layer genes
        possible_gene_choices = [{'type': 'optimizer'}]
        for layer in range(len(self.geneparam['layers'])):
            for gene in self.layer_genes:
                possible_gene_choices.append({'type': 'gene', 'layer': layer, 'gene': gene})

        # Add the chance of a new layer if not already at the maximum
        new_layer_possible = len(self.geneparam['layers']) < max(self.all_possible_genes['nb_layers'])
        if new_layer_possible:
            possible_gene_choices.append({'type': 'new_layer'})
        remove_layer_possible = len(self.geneparam['layers']) > 2
        if remove_layer_possible:
            possible_gene_choices.append({'type': 'remove_layer'})
        mutation = random.choice(possible_gene_choices)

        if mutation['type'] == 'optimizer':
            # Update optimizer gene
            current_value = self.geneparam['optimizer']
            possible_choices = copy.deepcopy(self.all_possible_genes['optimizer'])
            possible_choices.remove(current_value)
            self.geneparam['optimizer'] = random.choice(possible_choices)
        elif mutation['type'] == 'new_layer':
            # Add an entirely new layer
            new_layer = {}
            new_layer['nb_neurons'] = random.choice(self.all_possible_genes['nb_neurons'])
            new_layer['activation'] = random.choice(self.all_possible_genes['activation'])
            # Insert into a random position in the network
            self.geneparam['layers'].insert(len(self.geneparam['layers']) - 1, new_layer)
        elif mutation['type'] == 'remove_layer':
            # Remove a layer
            layer = random.randint(0, len(self.geneparam['layers']) - 1)
            del self.geneparam['layers'][layer]
        elif mutation['type'] == 'gene':
            # Update a layer gene
            layer_to_mutate = mutation['layer']
            gene_to_mutate = mutation['gene']
            # And then let's mutate one of the genes.
            # Make sure that this actually creates mutation
            current_value = self.geneparam['layers'][layer_to_mutate][gene_to_mutate]
            possible_choices = copy.deepcopy(self.all_possible_genes[gene_to_mutate])

            possible_choices.remove(current_value)

            self.geneparam['layers'][layer_to_mutate][gene_to_mutate] = random.choice(possible_choices)

        self.update_hash()

    def set_genes_to(self, geneparam):
        """Set genome properties.
        this is used when breeding kids
        Args:
            genome (dict): The genome parameters
        IMPROVE
        """
        self.geneparam = geneparam
        self.update_hash()

    def print_genome_ma(self):
        """Print out a genome."""
        print(self.geneparam)
        print("organism id: %d Mom and Dad: %d %d" % (self.organism_id, self.mom_id, self.dad_id))
        print("Hash: %s" % self.hash)