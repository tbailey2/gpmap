import numpy as np
from gpmap.gpm import GenotypePhenotypeMap
from gpmap import utils

class MountFujiSimulation(GenotypePhenotypeMap):
    """Constructs a genotype-phenotype map from a Mount Fuji model. [1]_

    A Mount Fuji sets a "global" fitness peak (max) on a single genotype in the space.
    The fitness goes down as a function of hamming distance away from this genotype,
    called a "fitness field". The strength (or scale) of this field is linear and
    depends on the parameters `field_strength`.

    Roughness can be added to the Mount Fuji model using a random `roughness` parameter.
    This assigns a random

    .. math::
        f(g) = \nu (g) - c \cdot d(g_0, g)

    where $\nu$ is the roughness parameter, $c$ is the field strength, and $d$ is the
    hamming distance between genotype $g$ and the reference genotype.

    Parameters
    ----------
    wildtype : str
        reference genotype to put the
    mutations : dict
        mutations alphabet for each site
    field_strength : float
        field strength
    roughness_range : tuple
        range of the randomly drawn roughness values to use.


    References
    ----------

    _ [1] Szendro, Ivan G., et al. "Quantitative analyses of empirical fitness landscapes."
        Journal of Statistical Mechanics: Theory and Experiment 2013.01 (2013): P01005.
    """
    def __init__(self, wildtype, mutations, field_strength=1, range=(0,1), *args, **kwargs):
        # build genotypes
        genotypes = utils.mutations_to_genotypes(wildtype, mutations)
        phenotypes = np.empty(len(genotypes), dtype=float)
        super(MountFujiSimulation, self).__init__(wildtype, genotypes,
            phenotypes,
            *args,
            **kwargs,
        )
        self._field_strength = field_strength
        self.build()

    @classmethod
    def from_length(cls, length, field_strength=1, *args, **kwargs):
        """ Create a simulate genotype-phenotype map from a given genotype length.

        Parameters
        ----------
        length : int
            length of genotypes
        alphabet_size : int (optional)
            alphabet size

        Returns
        -------
        self : GenotypePhenotypeSimulation
        """
        mutations = dict([(i,["0","1"]) for i in range(length)])
        wildtype = "".join([m[0] for m in mutations.values()])
        self = cls(wildtype, mutations, field_strength=field_strength, *args, **kwargs)
        return self

    @property
    def hamming(self):
        """Hamming distance from reference"""
        try:
            return self._hamming
        # calculate the hamming distance if not done already
        except AttributeError:
            hd = np.empty(self.n,dtype=int)
            for i, g in enumerate(self.genotypes):
                hd[i] = utils.hamming_distance(self.wildtype, g)
            self._hamming = hd
            return self._hamming

    @property
    def roughness(self):
        """Array of roughness values for all genotypes"""
        try:
            return self._roughness
        except AttributeError:
            return np.zeros(self.n)

    @property
    def field_strength(self):
        return self._field_strength

    @field_strength.setter
    def field_strength(self, c):
        self._field_strength = c
        self.build()

    def build(self):
        """Construct phenotypes using a rough Mount Fuji model."""
        self.phenotypes = self.roughness - self.field_strength * self.hamming

    def set_roughness(self, range=None):
        """Create a set of random values to add to the mount Fuji.

        Parameters
        ----------
        range : tuple
            range of values to sample from.
        """
        if range is None:
            self._roughness = np.zeros(self.n)
        else:
            if type(range) is not tuple:
                Exception("range must be a tuple pair")
            self._roughness = np.random.uniform(range[0], range[1], size=self.n)
        self.build()
