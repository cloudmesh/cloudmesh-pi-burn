from abc import ABC, abstractmethod

from cloudmesh.common.parameter import Parameter


class AbstractBurner(ABC):

    # @abstractmethod
    def cluster(self, arguments=None):
        """
        burns a list of cards from the inventory

        :param arguments:
        :type arguments:
        :return:
        :rtype:
        """
        burning = Parameter.expand(arguments.burning)
        for host in burning:
            arguments.burning = burning
            self.burn(arguments)

    @abstractmethod
    def burn(self, arguments=None):
        """
        burns a single card from the inventory

        :param arguments:
        :type arguments:
        :return:
        :rtype:
        """
        raise NotImplementedError

    def inventory(self, arguments=None):
        """
        Creates the inventory for a cluster

        :param arguments:
        :type arguments:
        :return:
        :rtype:
        """
        raise NotImplementedError
