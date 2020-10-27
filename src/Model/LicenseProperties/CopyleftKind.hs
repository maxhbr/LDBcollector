{-# LANGUAGE ExistentialQuantification #-}
{-# LANGUAGE TypeFamilies #-}
{-# LANGUAGE GADTs #-}
{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE DeriveGeneric #-}
module Model.LicenseProperties.CopyleftKind
    where

import qualified Prelude as P
import           MyPrelude

import qualified Data.Map as M

{-
    MaybeCopyleft
     | \
     |  - Copyleft
     |     | \
     |     |  - StrongCopyleft
     |     |     \
     |     |      - SaaSCopyleft
     |     |        \
     |     |         - MaximalCopyleft
     |     \
     |       - WeakCopyleft
     \
      - NoCopyleft
 -}
data CopyleftKind
  = StrongCopyleft
  | WeakCopyleft
  | SaaSCopyleft
  | MaximalCopyleft
  | Copyleft
  | MaybeCopyleft
  | NoCopyleft
  deriving (Eq, Show, Generic)
instance ToJSON CopyleftKind
instance Ord CopyleftKind where
  compare k1 k2 = let
      kOrder = M.fromList [ (MaximalCopyleft, 6 :: Int)
                          , (SaaSCopyleft, 5)
                          , (StrongCopyleft, 4)
                          , (WeakCopyleft, 3)
                          , (Copyleft, 2)
                          , (MaybeCopyleft, 1)
                          , (NoCopyleft, 0) ]
    in if k1 == k2
       then EQ
       else compare (kOrder M.! k1)  (kOrder M.! k2)
pessimisticMergeCopyleft :: CopyleftKind -> CopyleftKind -> CopyleftKind
-- pessimisticMergeCopyleft = max
pessimisticMergeCopyleft MaximalCopyleft _     = MaximalCopyleft
pessimisticMergeCopyleft _ MaximalCopyleft     = MaximalCopyleft
pessimisticMergeCopyleft SaaSCopyleft _        = SaaSCopyleft
pessimisticMergeCopyleft _ SaaSCopyleft        = SaaSCopyleft
pessimisticMergeCopyleft StrongCopyleft _      = StrongCopyleft
pessimisticMergeCopyleft _ StrongCopyleft      = StrongCopyleft
pessimisticMergeCopyleft WeakCopyleft _        = WeakCopyleft
pessimisticMergeCopyleft _ WeakCopyleft        = WeakCopyleft
pessimisticMergeCopyleft Copyleft _            = Copyleft
pessimisticMergeCopyleft _ Copyleft            = Copyleft
pessimisticMergeCopyleft MaybeCopyleft _       = MaybeCopyleft
pessimisticMergeCopyleft _ MaybeCopyleft       = MaybeCopyleft
pessimisticMergeCopyleft NoCopyleft NoCopyleft = NoCopyleft


