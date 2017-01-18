cdef class Atom:
    cdef public str atomSerial, name, resname, resChain, resnum, type, id, atomContent
    cdef public double x, y, z, mass
    cdef public bint protein

cdef class PDB:
    cdef public dict atoms
    cdef public list atomList, com, centroid
    cdef public double totalMass
    cdef public str pdb
